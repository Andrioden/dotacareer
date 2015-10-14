app.factory('WebSocketService', function($rootScope){
    var subscribers = [];

    var isWebSocketActivated = true;

    if (isWebSocketActivated) {
        var channel = new goog.appengine.Channel(websocketChannelToken);
        var socket = channel.open();

        socket.onopen = function(){
            console.log("WebSocket channel opened");
        }

        socket.onmessage = function(message){
            console.log("WebSocket channel message: " + message.data);
            var jsonData = JSON.parse(message.data);
            console.log("WebSocket channel message event: " + jsonData.event);
            console.log("WebSocket channel message object below");
            console.log(jsonData.object);

            // Notify Subscribers
            for (var i = 0; i < subscribers.length; i++) {
                if (subscribers[i].event == jsonData.event) subscribers[i].callback(jsonData.object)
            }
            // Potentially update rootscope object
            if (jsonData.object_path) updateRootScopeObject(jsonData.object_path, jsonData.object);
        }
    }

    // Allow other providers to subscribe to socket events
    return {
        subscribe: function(event, callback) {
            subscribers.push({event: event, callback: callback});
        }
    }

    // PRIVATE METHODS
    function updateRootScopeObject(objectPath, freshObject) {
        var objectPathParts = objectPath.split(".");
        var object = $rootScope;
        for (var i=0; i<objectPathParts.length; i++) {
            var nextPathPart = objectPathParts[i];

            if (object == null) {
                console.log("Object is null when next path is '" + nextPathPart + "'. Fullpath: '" + objectPath + "'. Ignoring object update.");
                return;
            }

            if (isArrayIdPath(nextPathPart)) {
                if (Array.isArray(object)) {

                    if (nextPathPart[0] == "-") {
                        nextPathPart = nextPathPart.substr(1,nextPathPart.length-1);
                        var id = getContentOfBrackets(nextPathPart);
                        deleteObjectInArrayByID(object, id);
                    }
                    else {
                        var id = getContentOfBrackets(nextPathPart);

                        var arrayObjectWithCorrectID = getObjectInArrayByID(object, id);
                        if (arrayObjectWithCorrectID == null) {
                            if (i == objectPathParts.length-1) {
                                object.push(freshObject);
                            }
                            else {
                                console.log("Bad objectPath '" + objectPath + "'. An array object with id '" +id + "' was not found and is not the last part of the object path. Ignoring object update.")
                                return;
                            }
                        }
                        else object = arrayObjectWithCorrectID;
                    }

                }
                else {
                    console.log("Bad objectPath '" + objectPath + "'. Previous object is not an array as next object path '" + nextPathPart + "' expects. Ignoring object update.");
                    return null;
                }
            }
            else { // Okei, then normal object change
                var prevObject = object; // Only for console.log purposes
                object = object[nextPathPart];
                if (!object) {
                    console.log("Bad objectPath " + objectPath + ". Null object found on next path '" + nextPathPart + "'. Ignoring object update. Might be an undetailed object. Print of object follows:");
                    console.log(prevObject)
                    return null;
                }
            }
        }

        if (object) {
            extendObjectWithObject(object, freshObject);
            $rootScope.$apply();
        }
        else console.log("No object found for " + objectPath);
    }

    function getContentOfBrackets(bracketsString) {
        return bracketsString.substr(1,bracketsString.length-2)
    }

    function deleteObjectInArrayByID(array, id) {
        for (var i=0; i<array.length; i++) {
            if (array[i].id == id) array.splice(i,1); // Works for int and string ids, since 1 == "1" equals true
        }
    }

    function getObjectInArrayByID(array, id) {
        for (var i=0; i<array.length; i++) {
            if (array[i].id == id) return array[i]; // Works for int and string ids, since 1 == "1" equals true
        }
        return null;
    }

    function isArrayIdPath(path) {
        if (path[0] == "[" && path[path.length-1] == "]") return true;
        if (path[0] == "-" && path[path.length-1] == "]") return true;
        return false;
    }
});