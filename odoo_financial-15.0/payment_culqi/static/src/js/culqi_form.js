odoo.define('payment_culqi.culqi_form', function(require){
    'use strict';

    var core = require('web.core');
    var _t = core._t;
    var PaymentForm = require('payment.payment_form');
    var Widget = require("web.Widget");

    var PaymentCulqiForm = Widget.extend({
	    events: {
            'click #culqi_pay_button': '_onClick'
	    },
    	init: function(parent, options){
            this._super.apply(this, arguments);
            this.options = _.extend(options || {}, {});
            new Card({
                form: document.querySelector('form'),
                container: '.card-wrapper',
            });
        },
        disableButton: function (button) {
            $(button).attr('disabled', true);
            $(button).children('.fa-lock').removeClass('fa-lock');
            $(button).prepend('<span class="o_loader"><i class="fa fa-refresh fa-spin"></i>&nbsp;</span>');
        },
        enableButton: function (button) {
            $(button).attr('disabled', false);
            $(button).children('.fa').addClass('fa-lock');
            $(button).find('span.o_loader').remove();
        },
  	    _onClick: function(e){
            e.preventDefault();
            var self = this;
            var el_form = this.$el;
            var button = e.target;
            this.disableButton(button);
            el_form.find('input').each(function(){
                var my_element = this;
                if(!my_element.checkValidity()){
                    $(my_element).addClass('is-invalid');
                }else{
                    $(my_element).removeClass('is-invalid');
                }
                if($(my_element).attr('name') == 'expiry' && $(my_element).val().length != 7){
                    $(my_element).addClass('is-invalid');
                }
            })
            if ($(el_form).find('.is-invalid').length){
                this.enableButton(button);
                e.stopPropagation();
                return false;
            }            
            $('#remove_me').remove();
        },
    });

    $(function () {
        if (!$('form[name=o_culqi_form]').length) {
            return;
        }
        $('form[name=o_culqi_form]').each(function () {
            var $elem = $(this);
            var form = new PaymentCulqiForm(null, $elem.data());
            form.attachTo($elem);
        });
    });
});
