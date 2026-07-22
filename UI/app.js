Dropzone.autoDiscover = false;

const PLAYER_LABELS = {
    lionel_messi: "Lionel Messi",
    maria_sharapova: "Maria Sharapova",
    roger_federer: "Roger Federer",
    serena_williams: "Serena Williams",
    virat_kohli: "Virat Kohli"
};

function init() {
    let selectedFile = null;
    const $btn = $("#submitBtn");

    // Block dragging roster images into the dropzone (upload from disk only).
    const roster = document.getElementById("roster");
    if (roster) {
        roster.addEventListener("dragstart", function (event) {
            event.preventDefault();
        });
    }

    const dz = new Dropzone("#dropzone", {
        url: "/",
        maxFiles: 1,
        addRemoveLinks: true,
        dictDefaultMessage: "Drop image here or click to browse",
        autoProcessQueue: false,
        clickable: true,
        acceptedFiles: "image/*",
        thumbnailWidth: 260,
        thumbnailHeight: 260,
        dictRemoveFile: "Remove photo",
        accept: function (file, done) {
            // Reject non-file drops (e.g. page images / URL drags).
            const isRealFile = file && (file instanceof File || (file.size > 0 && file.type));
            if (!isRealFile) {
                done("Please upload an image from your computer.");
                return;
            }
            done();
        },
        init: function () {
            this.on("drop", function (event) {
                const files = event.dataTransfer && event.dataTransfer.files;
                const hasLocalFiles = files && files.length > 0;
                const types = event.dataTransfer ? Array.from(event.dataTransfer.types || []) : [];
                const looksLikePageImage = types.includes("text/uri-list") || types.includes("text/html");

                if (!hasLocalFiles || (looksLikePageImage && !hasLocalFiles)) {
                    event.preventDefault();
                    event.stopPropagation();
                    showError("Please upload an image from your computer (click or drag a file from your device).");
                }
            });

            this.on("addedfile", function (file) {
                if (this.files.length > 1) {
                    this.removeFile(this.files[0]);
                }
                selectedFile = file;
                hideError();
            });

            this.on("error", function (file, message) {
                if (file) {
                    this.removeFile(file);
                }
                selectedFile = null;
                showError(typeof message === "string" ? message : "Please upload an image from your computer.");
            });

            this.on("removedfile", function (file) {
                if (selectedFile === file) {
                    selectedFile = null;
                }
            });
        }
    });

    function showError(message) {
        $("#emptyState").hide();
        $("#resultHolder").attr("hidden", true).hide();
        $("#divClassTable").attr("hidden", true).hide();
        $(".athlete-card").removeClass("is-winner");
        $("#error").text(message).prop("hidden", false).show();
    }

    function hideError() {
        $("#error").prop("hidden", true).hide();
    }

    function setLoading(isLoading) {
        $btn.toggleClass("is-loading", isLoading);
        $btn.prop("disabled", isLoading);
        $btn.find(".btn-label").text(isLoading ? "Classifying…" : "Classify athlete");
    }

    function resetScores() {
        Object.keys(PLAYER_LABELS).forEach((key) => {
            $(`#score_${key}`).text("0%");
            $(`#bar_${key}`).css("width", "0%");
            $(`[data-score="${key}"]`).removeClass("is-top");
        });
    }

    function handleResponse(data) {
        if (!data || data.length === 0) {
            showError("Could not classify this image. Try a clearer face photo in JPG or PNG format.");
            return;
        }

        let bestMatch = null;
        let bestScore = -1;

        data.forEach((item) => {
            const maxProbability = Math.max(...item.class_probability);
            if (maxProbability > bestScore) {
                bestScore = maxProbability;
                bestMatch = item;
            }
        });

        if (!bestMatch) {
            showError("Could not find a confident prediction for this image.");
            return;
        }

        // Always derive the winner from probabilities so the name matches the bars.
        const classDictionary = bestMatch.class_dictionary;
        const ranked = Object.keys(classDictionary)
            .map((personName) => ({
                name: personName,
                score: Number(bestMatch.class_probability[classDictionary[personName]] || 0)
            }))
            .sort((a, b) => b.score - a.score);

        const playerKey = ranked[0].name;
        bestScore = ranked[0].score;
        const secondScore = ranked[1] ? ranked[1].score : 0;

        const playerCard = $(`[data-player="${playerKey}"]`);
        if (!playerCard.length) {
            showError("Prediction returned an unknown player label.");
            return;
        }

        hideError();
        $("#emptyState").hide();
        $(".athlete-card").removeClass("is-winner");
        playerCard.addClass("is-winner");

        const sport = playerCard.data("sport") || "Athlete";
        const imgSrc = playerCard.find("img").attr("src");
        const displayName = PLAYER_LABELS[playerKey] || playerKey;
        const isLowConfidence = bestScore < 45 || (bestScore - secondScore) < 5;
        const confidenceNote = isLowConfidence
            ? `<p class="confidence-note">Low confidence — try a clearer front-facing face photo.</p>`
            : "";

        $("#resultHolder")
            .html(`
                <img src="${imgSrc}" alt="${displayName}">
                <div class="result-copy">
                    <h3>${displayName}</h3>
                    <p>${sport} · best match from the roster</p>
                    <div class="confidence">${bestScore.toFixed(1)}% confidence</div>
                    ${confidenceNote}
                </div>
            `)
            .prop("hidden", false)
            .show();

        resetScores();
        $("#divClassTable").prop("hidden", false).show();

        for (const personName in classDictionary) {
            const index = classDictionary[personName];
            const probabilityScore = Number(bestMatch.class_probability[index] || 0);
            $(`#score_${personName}`).text(`${probabilityScore.toFixed(1)}%`);
            const $bar = $(`#bar_${personName}`);
            $bar.css("width", "0%");
            void $bar[0].offsetWidth;
            $bar.css("width", `${Math.min(probabilityScore, 100)}%`);
        }

        $(`[data-score="${playerKey}"]`).addClass("is-top");
    }

    function classifyCurrentFile() {
        if (!selectedFile) {
            showError("Please upload an image first.");
            return;
        }

        if (!selectedFile.dataURL) {
            showError("Unable to read the selected image. Please try another file.");
            return;
        }

        setLoading(true);

        $.post("/classify_image", {
            image_data: selectedFile.dataURL
        })
            .done(function (data) {
                if (data && data.error) {
                    showError(data.error);
                    return;
                }
                handleResponse(data);
            })
            .fail(function (xhr) {
                let payload = xhr.responseJSON;
                if (!payload && xhr.responseText) {
                    try {
                        payload = JSON.parse(xhr.responseText);
                    } catch (e) {
                        payload = null;
                    }
                }
                if (payload && payload.error) {
                    showError(payload.error);
                    return;
                }
                const status = xhr.status ? ` (HTTP ${xhr.status})` : "";
                showError(`Server error${status}. Make sure the Flask app is running and try again.`);
            })
            .always(function () {
                setLoading(false);
            });
    }

    $btn.on("click", classifyCurrentFile);
}

$(document).ready(function () {
    $("#error").hide();
    $("#resultHolder").hide();
    $("#divClassTable").hide();
    init();
});
