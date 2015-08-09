function HubsAPI(url, serverTimeout) {
    var messageID = 0;
    var returnFunctions = {};
    var respondTimeout = (serverTimeout || 5) * 1000;
    var thisApi = this;
    url = url || "";

    this.wsClient = new WebSocket(url);

    var constructMessage = function (hubName, functionName, args) {
        args = Array.prototype.slice.call(args);
        var id = messageID++;
        var body = {"hub": hubName, "function": functionName, "args": args, "ID": id};
        thisApi.wsClient.send(JSON.stringify(body));
        return {done: getReturnFunction(id)}
    };
    var getReturnFunction = function (ID) {
        return function (onSuccess, onError) {
            if (returnFunctions[ID] == undefined)
                returnFunctions[ID] = {};
            var f = returnFunctions[ID];
            f.onSuccess = function () {
                onSuccess.apply(onSuccess, arguments);
                delete returnFunctions[ID]
            };
            f.onError = function () {
                onError.apply(onError, arguments);
                delete returnFunctions[ID]
            };
            //check returnFunctions, memory leak
            setTimeout(function () {
                if (returnFunctions[ID] && returnFunctions[ID].onError)
                    returnFunctions[ID].onError("timeOut Error");
            }, respondTimeout)
        }
    };
    this.wsClient.onmessage = function (ev) {
        var f,
            msgObj;
        try {
            msgObj = JSON.parse(ev.data);
            if (msgObj.hasOwnProperty("replay")) {
                f = returnFunctions[msgObj.ID];
                if (msgObj.success && f != undefined && f.onSuccess != undefined)
                    f.onSuccess(msgObj.replay);
                else if (f != undefined && f.onError != undefined)
                    f.onError(msgObj.replay)
            } else {
                f = thisApi[msgObj.hub].client[msgObj.function];
                f.apply(f, msgObj.args)
            }
        } catch (err) {
            this.onMessageError(err)
        }
    };
    this.wsClient.onMessageError = function (error) {
    };
    
    this.SyncHub = {};
    this.SyncHub.server = {
        __HUB_NAME : "SyncHub",
        
        phoneNumbers : function (phoneNumberArray){
            
            return constructMessage(this.__HUB_NAME, "phoneNumbers",arguments);
        }
    }
    this.SyncHub.client = {}
    this.LoggingHub = {};
    this.LoggingHub.server = {
        __HUB_NAME : "LoggingHub",
        
        logIn : function (phoneNumber, gcmId, name, email){
            arguments[0] = phoneNumber == undefined ? None : phoneNumber;
			arguments[1] = gcmId == undefined ? None : gcmId;
            return constructMessage(this.__HUB_NAME, "logIn",arguments);
        }
    }
    this.LoggingHub.client = {}
    this.TaskHub = {};
    this.TaskHub.server = {
        __HUB_NAME : "TaskHub",
        
        getNotUpdatedTasks : function (since, userId){
            
            return constructMessage(this.__HUB_NAME, "getNotUpdatedTasks",arguments);
        },

        syncTask : function (newTask){
            
            return constructMessage(this.__HUB_NAME, "syncTask",arguments);
        },

        syncTasks : function (tasks){
            
            return constructMessage(this.__HUB_NAME, "syncTasks",arguments);
        }
    }
    this.TaskHub.client = {}
    this.UtilsHub = {};
    this.UtilsHub.server = {
        __HUB_NAME : "UtilsHub",
        
        setID : function (id){
            
            return constructMessage(this.__HUB_NAME, "setID",arguments);
        }
    }
    this.UtilsHub.client = {}
    this.PlaceHub = {};
    this.PlaceHub.server = {
        __HUB_NAME : "PlaceHub",
        
        createPlace : function (newPlace){
            
            return constructMessage(this.__HUB_NAME, "createPlace",arguments);
        },

        getPlaces : function (ownerID){
            
            return constructMessage(this.__HUB_NAME, "getPlaces",arguments);
        },

        syncPlace : function (newPlace){
            
            return constructMessage(this.__HUB_NAME, "syncPlace",arguments);
        },

        updatePlace : function (newPlace){
            
            return constructMessage(this.__HUB_NAME, "updatePlace",arguments);
        }
    }
    this.PlaceHub.client = {}
}
    