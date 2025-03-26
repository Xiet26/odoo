odoo.define('custom_social_float.social_float', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.SocialFloatButtons = publicWidget.Widget.extend({
        selector: '.social-float-container',
        
        start: function () {
            var self = this;
            return this._rpc({
                model: 'social.float',
                method: 'search_read',
                domain: [['is_active', '=', true]],
                fields: ['zalo_link', 'facebook_link', 'phone_number', 'zalo_icon', 
                        'facebook_icon', 'phone_icon', 'button_color', 'icon_color'],
            }).then(function (result) {
                if (result && result.length > 0) {
                    var data = result[0];
                    self._renderButtons(data);
                }
            });
        },

        _renderButtons: function (data) {
            var container = this.$el;

            // Zalo Button
            if (data.zalo_link) {
                this._createButton(container, data.zalo_icon, data.zalo_link, data.button_color, data.icon_color);
            }

            // Facebook Button
            if (data.facebook_link) {
                this._createButton(container, data.facebook_icon, data.facebook_link, data.button_color, data.icon_color);
            }

            // Phone Button
            if (data.phone_number) {
                this._createButton(container, data.phone_icon, 'tel:' + data.phone_number, data.button_color, data.icon_color);
            }
        },

        _createButton: function (container, icon, link, bgColor, iconColor) {
            var button = $('<a>', {
                class: 'social-float-button',
                href: link,
                target: '_blank',
                style: 'background-color: ' + bgColor,
            });

            // Parse SVG string and set icon color
            var tempDiv = document.createElement('div');
            tempDiv.innerHTML = icon;
            var svg = $(tempDiv).find('svg')[0];
            if (svg) {
                $(svg).find('path').attr('fill', iconColor);
                button.append(svg);
            }

            container.append(button);
        },
    });
}); 