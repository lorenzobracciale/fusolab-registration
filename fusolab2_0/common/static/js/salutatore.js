$(function(){
    /*
    if (window.localStorage.getItem("chat-simple") != null){
        var messages = window.localStorage.getItem("chat-simple").split(",");
        for (var i = 0; i < messages.length; i++){
            localStorage.removeItem("chat-simple-" + messages[i]);
        }
    }
    */

    var Message = Backbone.Model.extend({

        defaults: function() {
            return {
                text: "empty...",
                image: avatar_url,
                date: "Or ora",
                sender: myname,
                order: Messages.nextOrder()
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

    var MessageList = Backbone.Collection.extend({
        model: Message,
        //localStorage: new Backbone.LocalStorage("chat-simple"),
        url: "/salutatore/sentences_list/",
        nextOrder: function() {
            if (!this.length) return 1;
            return this.last().get('order') + 1;
        },
        comparator: function(message) {
            return message.get('order');
        }

    });

    var Messages = new MessageList;

    var MessageView = Backbone.View.extend({

        className: 'salutatore-message',

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

    var AppView = Backbone.View.extend({

        el: $("#salutatore"),

        events: {
            "keypress #new-message":  "createOnEnter",
            "click #new-message-btn": "createOnClick"
        },

        initialize: function() {

            this.input = this.$("#new-message");

            this.listenTo(Messages, 'add', this.addOne);
            //this.listenTo(Messages, 'all', this.render);

            //Messages.fetch(); 
             
            Messages.fetch({success: function(){
                 Salutatore.render();
            }});
            
            

        },
         
        render: function() {
            Messages.each(function( item ) {
                this.addOne( item );
            }, this );
        },
        
        

        addOne: function(message) {
            var view = new MessageView({model: message});
            this.$("#salutatore-messages").append(view.render().el);
        },

        createOnEnter: function(e) {
            if (Messages.length < 10){
                // e.preventDefault();
                if (e.keyCode != 13) return;
                if (!this.input.val()) return;

                Messages.create({text: this.input.val()});
                this.input.val('');

                var view = this.$("#salutatore-messages")[0];
                view.scrollTop = view.scrollHeight;
            }
        },

        createOnClick: function(e) {
            if (Messages.length < 10){
                if (!this.input.val()) return;

                Messages.create({text: this.input.val()});
                this.input.val('');

                var view = this.$("#salutatore-messages")[0];
                view.scrollTop = view.scrollHeight;
            }
        }

    });

    // Finally, we kick things off by creating the **App**.
    var Salutatore = new AppView;
    setInterval(function(){
        Messages.reset();
         
        Messages.fetch({success: function(){
             Salutatore.$("#salutatore-messages").empty();
             Salutatore.render();
        }});
    },60000); // poll every minute

    Backbone.originalSync2 = Backbone.sync;
    Backbone.sync = function (method, model, options) {
        var originalSuccess, originalError;
        originalError = options.error;
        options.error = function (model, xhr, options) {
            $("#ecce-homo").attr("src", "http://soci.fusolab.net/static/images/ecce-homo.jpg");
            $("#myModal").modal('show');
        }
        Backbone.originalSync2(method, model, options);
    }


});
