$(function(){
    /*
    if (window.localStorage.getItem("chat-simple") != null){
        var messages = window.localStorage.getItem("chat-simple").split(",");
        for (var i = 0; i < messages.length; i++){
            localStorage.removeItem("chat-simple-" + messages[i]);
        }
    }
    */

    var LedMessage = Backbone.Model.extend({

        defaults: function() {
            return {
                text: "empty...",
                image: avatar_url,
                date: "Or ora",
                sender: myname,
                order: LedMessages.nextOrder()
            };
        },

        initialize: function() {
            if (!this.get("text")) {
                this.set({"text": this.defaults().text});
            }
            if (!this.get("date")) {
                this.set({"date": this.defaults().date});
            }
        }

    });

    var LedMessageList = Backbone.Collection.extend({
        model: LedMessage,
        //localStorage: new Backbone.LocalStorage("chat-simple"),
        url: "/baraled/sentences_list/",
        nextOrder: function() {
            if (!this.length) return 1;
            return this.last().get('order') + 1;
        },
        comparator: function(message) {
            return message.get('order');
        }

    });

    var LedMessages = new LedMessageList;

    var LedMessageView = Backbone.View.extend({

        className: 'baraled-message',

        template: _.template($('#message-template').html()),

        initialize: function() {
            this.listenTo(this.model, 'change', this.render);
        },

        // Re-render the titles of the todo item.
        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        }

    });

    var LedAppView = Backbone.View.extend({

        el: $("#baraled"),

        events: {
            "keypress #new-message2":  "createOnEnter",
            "click #new-message-btn2": "createOnClick"
        },

        initialize: function() {

            this.input = this.$("#new-message2");

            this.listenTo(LedMessages, 'add', this.addOne);
            //this.listenTo(Messages, 'all', this.render);

            //Messages.fetch(); 
             
            LedMessages.fetch({success: function(){
                 BaraLed.render();
            }});
            
            

        },
         
        render: function() {
            LedMessages.each(function( item ) {
                this.addOne( item );
            }, this );
        },
        
        

        addOne: function(message) {
            var view = new LedMessageView({model: message});
            this.$("#baraled-messages").append(view.render().el);
        },

        createOnEnter: function(e) {
            if (LedMessages.length < 10){
                // e.preventDefault();
                if (e.keyCode != 13) return;
                if (!this.input.val()) return;

                LedMessages.create({text: this.input.val()});
                this.input.val('');

                var view = this.$("#baraled-messages")[0];
                view.scrollTop = view.scrollHeight;
            }
        },

        createOnClick: function(e) {
            if (LedMessages.length < 10){
                if (!this.input.val()) return;

                LedMessages.create({text: this.input.val()});
                this.input.val('');

                var view = this.$("#baraled-messages")[0];
                view.scrollTop = view.scrollHeight;
            }
        }

    });

    // Finally, we kick things off by creating the **App**.
    var BaraLed = new LedAppView;
    setInterval(function(){
        LedMessages.reset();
         
        LedMessages.fetch({success: function(){
             BaraLed.$("#baraled-messages").empty();
             BaraLed.render();
        }});
    },60000); // poll every minute

    Backbone.originalSync = Backbone.sync;
    Backbone.sync = function (method, model, options) {
        var originalSuccess, originalError;
        originalError = options.error;
        options.error = function (model, xhr, options) {
            $("#ecce-homo").attr("src", "/static/images/ecce-homo.jpg");
            $("#myModal").modal('show');
        }
        Backbone.originalSync(method, model, options);
    }

});
