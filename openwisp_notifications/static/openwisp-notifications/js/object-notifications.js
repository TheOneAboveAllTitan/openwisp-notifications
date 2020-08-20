'use strict';

(function ($) {
    let objectNotificationBell =  `
        <div id="ow-object-notify" class="ow-object-notify ow-object-notify-bell "></div>
        <div class="object-notification-container ow-hide">
            <div data-days="1"><p>1 Day</p></div>
            <div data-days="7"><p>1 Week</p></div>
            <div data-days="30"><p>1 Month</p></div>
            <div data-days="0"><p>Forever</p></div>
        </div>
    `
    $(document).ready(function () {
        $('.breadcrumbs').append(objectNotificationBell);
        initObjectNotificationDropdown($);
        $('.breadcrumbs').on('click', '.object-notification-container > div', function(e){
            e.stopPropagation();
            let days_offset = $(this).data('days'), date = new Date();
            date.setDate(date.getDate + days_offset)
            $('.object-notification-container').toggleClass('ow-hide');
        })
    });
})(django.jQuery);

function initObjectNotificationDropdown($){
    $('.breadcrumbs').on('click', '.ow-object-notify', function(e){
        e.stopPropagation();
        $('.object-notification-container').toggleClass('ow-hide');
    })
    $(document).click(function (e) {
        e.stopPropagation();
        // Check if the clicked area is dropDown or not
        if ($('.object-notification-container').has(e.target).length === 0) {
            $('.object-notification-container').addClass('ow-hide');
        }
    });
}
