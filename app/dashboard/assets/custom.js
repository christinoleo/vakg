if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.clientside = {
    resize: function (value) {
        console.log('resizing...'); // for testing
        setTimeout(function () {
            window.dispatchEvent(new Event('resize'));
            console.log('fired resize');
        }, 500);
        return null;
    },

    resize2: function (children, className, _id) {
        let element = document.getElementById(_id);
        // console.log("resizingV2...", a, a.children, children); // for testing
        element.childNodes.forEach(n => {
            n.style.height = n.scrollHeight + 'px';
            // console.log(n.offsetHeight, n.clientHeight, n.scrollHeight, n.innerHeight);
        });
        setTimeout(function () {
            window.dispatchEvent(new Event('resize'));
            console.log('fired resizeV2');
        }, 500);
        return className; // for testing
    },
};