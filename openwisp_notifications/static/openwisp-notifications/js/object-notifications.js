'use strict';
(function ($) {
    $(document).ready(function () {
        if (owIsChangeForm !== true){
            // Don't add object notification widget if
            // it is not a change form.
            return;
        }
        $('.object-tools').prepend(getObjectNotificationComponent());
        initObjectNotificationDropdown($);
        addObjectNotificationHandlers($);
        addObjectNotificationWSHandlers($);
    });
})(django.jQuery);

function getObjectNotificationComponent(){
    return `
        <div id="ow-object-notify" class="ow-object-notify button">
        <div class="ow-icon ow-object-notify-bell"></div>
            <p id="ow-unsubscribe-label">Unsubscribe</p>
        </div>
        <div class="ow-object-notification-container ow-hide">
            <p id="ow-notification-help-text">Disable notifications for</p>
            <div data-days=0 class="ow-hide" id="ow-enable-notification"><p>Enable Notifications</p></div>
            <div data-days=1 class="ow-notification-option"><p>1 Day</p></div>
            <div data-days=7 class="ow-notification-option"><p>1 Week</p></div>
            <div data-days=30 class="ow-notification-option"><p>1 Month</p></div>
            <div data-days=-1 class="ow-notification-option"><p>Forever</p></div>
        </div>
    `;
}
function initObjectNotificationDropdown($) {
    $(document).on('click', '.ow-object-notify', function (e) {
        e.stopPropagation();
        $('.ow-object-notification-container').toggleClass('ow-hide');
    });
    $(document).click(function (e) {
        e.stopPropagation();
        // Check if the clicked area is dropDown or not
        if ($('.ow-object-notification-container').has(e.target).length === 0) {
            $('.ow-object-notification-container').addClass('ow-hide');
        }
    });
}

function addObjectNotificationHandlers($) {
    // Click handler for disabling notifications
    $(document).on('click', 'div.ow-notification-option', function (e) {
        e.stopPropagation();
        let daysOffset = $(this).data('days'), validTill;
        if (daysOffset === -1) {
            validTill = undefined;
        } else {
            validTill = new Date();
            validTill.setDate(validTill.getDate() + daysOffset);
            validTill = validTill.toISOString();
        }

        $.ajax({
            type: 'PUT',
            url: getAbsoluteUrl(`/api/v1/notification/ignore/${owNotifyAppLabel}/${owNotifyModelName}/${owNotifyObjectId}/`),
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            xhrFields: {
                withCredentials: true
            },
            data: {
                valid_till: validTill,
            },
            crossDomain: true,
            success: function () {
                updateObjectNotificationHelpTest($, validTill);
            },
            error: function (error) {
                throw error;
            },
        });
    });

    // Click handler for enabling notifications
    $(document).on('click', '#ow-enable-notification', function (e) {
        e.stopPropagation();
        $.ajax({
            type: 'DELETE',
            url: getAbsoluteUrl(`/api/v1/notification/ignore/${owNotifyAppLabel}/${owNotifyModelName}/${owNotifyObjectId}/`),
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            xhrFields: {
                withCredentials: true
            },
            crossDomain: true,
            success: function () {
                $('#ow-object-notify > div.ow-icon').removeClass('ow-object-notify-slash-bell');
                $('#ow-object-notify > div.ow-icon').addClass('ow-object-notify-bell');
                $('#ow-unsubscribe-label').html('Unsubscribe');

                $('#ow-notification-help-text').html(`Disable notifications for`);
                $('#ow-enable-notification').addClass('ow-hide');
                $('.ow-notification-option').removeClass('ow-hide');
            },
            error: function (error) {
                throw error;
            },
        });
    });
}

function addObjectNotificationWSHandlers($) {
    notificationSocket.addEventListener('open', function () {
        let data = {
            type: 'object_notification',
            object_id: owNotifyObjectId,
            app_label: owNotifyAppLabel,
            model_name: owNotifyModelName
        };
        notificationSocket.send(JSON.stringify(data));
    });

    notificationSocket.addEventListener('message', function (e) {
        let data = JSON.parse(e.data);
        if (data.type !== 'object_notification') {
            return;
        }
        if (data.hasOwnProperty('valid_till')) {
            updateObjectNotificationHelpTest($, data.valid_till);
        }
    });
}

function updateObjectNotificationHelpTest($, validTill) {
    let disabledText,
        lang = navigator.language || navigator.userLanguage;
    if ((validTill === null) || (validTill === undefined)){
        disabledText = `Disabled forever`;
    } else {
        validTill = new Date(validTill);
        validTill = validTill.toLocaleDateString(
            lang, {
                day: 'numeric',
                month: 'short',
                year: 'numeric'
            }
        );
        disabledText = `Disabled till ${validTill}`;
    }

    $('#ow-notification-help-text').html(disabledText);
    $('#ow-enable-notification').removeClass('ow-hide');
    $('.ow-notification-option').addClass('ow-hide');

    $('#ow-object-notify > div.ow-icon').removeClass('ow-object-notify-bell');
    $('#ow-object-notify > div.ow-icon').addClass('ow-object-notify-slash-bell');
    $('#ow-unsubscribe-label').html('Unsubscribed');
}
