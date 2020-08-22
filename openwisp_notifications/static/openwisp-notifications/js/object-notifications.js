'use strict';
(function ($) {
    $(document).ready(function () {
        if (typeof owIsChangeForm === null){
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
    <div class="ow-object-notification-container">
        <div id="ow-object-notify" class="ow-object-notify button" title="You are receiving notifications for this object.">
        <div class="ow-icon ow-object-notify-bell"></div>
            <p id="ow-unsubscribe-label">Unsubscribe</p>
        </div>
        <div class="ow-object-notification-option-container ow-hide">
            <p id="ow-notification-help-text">Disable notifications for</p>
            <div data-days=0 class="ow-hide ow-notification-option" id="ow-enable-notification"><p>Enable Notifications</p></div>
            <div data-days=1 class="ow-notification-option disable-notification"><p>1 Day</p></div>
            <div data-days=7 class="ow-notification-option disable-notification"><p>1 Week</p></div>
            <div data-days=30 class="ow-notification-option disable-notification"><p>1 Month</p></div>
            <div data-days=-1 class="ow-notification-option disable-notification"><p>Forever</p></div>
            <div id="ow-object-notification-loader" class="ow-hide"><div class="loader"></div></div>
        </div>
    </div>
    `;
}
function initObjectNotificationDropdown($) {
    $(document).on('click', '.ow-object-notify', function (e) {
        e.stopPropagation();
        $('.ow-object-notification-option-container').toggleClass('ow-hide');
    });
    $(document).click(function (e) {
        e.stopPropagation();
        // Check if the clicked area is dropDown or not
        if ($('.ow-object-notification-option-container').has(e.target).length === 0) {
            $('.ow-object-notification-option-container').addClass('ow-hide');
        }
    });
}

function addObjectNotificationHandlers($) {
    // Click handler for disabling notifications
    $(document).on('click', 'div.ow-notification-option.disable-notification', function (e) {
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
            beforeSend: function(){
                $('.ow-object-notification-option-container > div').addClass('ow-hide')
                $('#ow-object-notification-loader').removeClass('ow-hide');
            },
            data: {
                valid_till: validTill,
            },
            crossDomain: true,
            success: function () {
                updateObjectNotificationHelpTest($, validTill);
                $('#ow-object-notification-loader').addClass('ow-hide');
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
            beforeSend: function(){
                $('.ow-object-notification-option-container > div').addClass('ow-hide')
                $('#ow-object-notification-loader').removeClass('ow-hide');
            },
            crossDomain: true,
            success: function () {
                $('#ow-object-notify > div.ow-icon').removeClass('ow-object-notify-slash-bell');
                $('#ow-object-notify > div.ow-icon').addClass('ow-object-notify-bell');
                $('#ow-unsubscribe-label').html('Unsubscribe');

                $('#ow-notification-help-text').html(`Disable notifications for`);
                $('#ow-object-notification-loader').addClass('ow-hide');
                $('.ow-notification-option.disable-notification').removeClass('ow-hide');
            },
            error: function (error) {
                throw error;
            },
        });
    });
}

function addObjectNotificationWSHandlers($) {
    if (notificationSocket.readyState === 1) {
        openHandler()
    }
    notificationSocket.addEventListener('open', openHandler);

    notificationSocket.addEventListener('message', function (e) {
        let data = JSON.parse(e.data);
        if (data.type !== 'object_notification') {
            return;
        }
        if (data.hasOwnProperty('valid_till')) {
            updateObjectNotificationHelpTest($, data.valid_till);
        }
    });

    function openHandler() {
        let data = {
            type: 'object_notification',
            object_id: owNotifyObjectId,
            app_label: owNotifyAppLabel,
            model_name: owNotifyModelName
        };
        notificationSocket.send(JSON.stringify(data));
    }
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
    $('.ow-notification-option.disable-notification').addClass('ow-hide');

    $('#ow-object-notify > div.ow-icon').removeClass('ow-object-notify-bell');
    $('#ow-object-notify > div.ow-icon').addClass('ow-object-notify-slash-bell');
    $('#ow-unsubscribe-label').html('Unsubscribed');
    $('#ow-unsubscribe-label').prop('title', 'You have disabled notifications for this object.');
}
