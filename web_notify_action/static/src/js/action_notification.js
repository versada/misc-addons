openerp.web_notify_action = function (instance) {
    'use strict';
    instance.web.Notification.include({
        notify: function(title, text, sticky) {
            // Override of the original function to allow numeric timeout
            // duration to be passed via `sticky` parameter. If `sticky` is not
            // a number then the original behavior is invoked.
            var opts = {};
            if (typeof sticky === "number") {
                opts.expires = sticky;
            } else {
                sticky = !!sticky;
                if (sticky) {
                    opts.expires = false;
                }
            }
            return this.$el.notify('create', {
                title: title,
                text: text
            }, opts);
        },
    });

    instance.web.WebClient.include({
        on_notify_action_notification: function(notification) {
            if (notification[0][1] === 'web_notify_action.notify_action') {
                this.action_manager.do_action(notification[1]);
            }
        },
        show_application: function() {
            return $.when(
                this._super.apply(this, arguments)
            ).then((function() {
                instance.bus.bus.on('notification', this, this.on_notify_action_notification);
                instance.bus.bus.start_polling();
            }).bind(this));
        }
    });

};
