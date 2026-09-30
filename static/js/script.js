document.addEventListener("DOMContentLoaded", function () {

    const textareas = document.querySelectorAll("textarea");

    textareas.forEach(function (textarea) {

        textarea.addEventListener("input", function () {

            const maxLength = textarea.getAttribute("maxlength");

            if (maxLength) {
                console.log(
                    textarea.value.length + "/" + maxLength
                );
            }

        });

    });


    const messages = document.querySelectorAll(".message");

    messages.forEach(function (message) {

        setTimeout(function () {
            message.style.opacity = "0";

            setTimeout(function () {
                message.remove();
            }, 500);

        }, 3000);

    });

});