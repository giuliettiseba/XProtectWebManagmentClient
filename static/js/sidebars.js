/* global bootstrap: false */
(function () {
    'use strict'
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl)
    })

    $(document).ready(function () {
        $('li').click(function (e) {
            $("a").removeClass("active");
            $(this).find("a").addClass("active");
            const selected = $(this).find("a").text().replace(/\s/g, '').toLowerCase();
            showContent(selected)
        });
    });

    function showContent(theObject) {


        $.ajax({
            url: `/` + theObject,
            success: function (data) {
                // console.log(data)
                $(".detaills").html(data)
            }
        });
    }

})()
