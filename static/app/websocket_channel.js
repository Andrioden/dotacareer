app.factory('WebSocketService', function(){
    var subscribers = [];

    var channel = new goog.appengine.Channel(websocket_channel_token);
    var socket = channel.open();

    socket.onopen = function(){
        console.log("WebSocket channel opened");
    }

    socket.onmessage = function(message){
        console.log("WebSocket channel message:" + message.data);
        var jsonData = JSON.parse(message.data);
        for (var i = 0; i < subscribers.length; i++) {
            if (subscribers[i].type == jsonData.type) subscribers[i].callback(jsonData.value)
        }
    }

    // Allow other providers to subscribe to socket events
    return {
        subscribe: function(type, callback) {
            subscribers.push({type: type, callback: callback});
        }
    }
});