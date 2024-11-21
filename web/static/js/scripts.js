function showLoader() {
    // Pokaż loader
    const loaderWrapper = document.getElementById("container-loader-wrapper");
    if (loaderWrapper) {
        loaderWrapper.style.display = "flex";
    }

    // Ukryj loader po upływie czasu
    setTimeout(() => {
        if (loaderWrapper) {
            loaderWrapper.style.display = "none";
        }
    }, {{ wait_time }});
}

function animateProgressBars() {
    const bars = ['fill1', 'fill2', 'fill3'];
    bars.forEach(barId => {
        const bar = document.getElementById(barId);
        if (bar) {
            bar.style.height = bar.getAttribute("data-height");
        }
    });
}

function scrollToBottom() {
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth'
    });
}
