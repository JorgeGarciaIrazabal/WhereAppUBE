package C:/Software Projects/WhereAppU/app/src/main/java/com/application/jorge/whereappu/WebSocket;
import com.google.gson.Gson;
import org.json.simple.JSONArray;
import org.json.JSONException;
import org.json.simple.JSONObject;
import java.net.URISyntaxException;
import C:/Software Projects/WhereAppU/app/src/main/java/com/application/jorge/whereappu/WebSocket.ClientHubs.*;
public class WSHubsApi {//TODO: do not use static functions, we might want different connections
    private static Gson gson = new Gson();
    public static WSConnection wsClient;

    public WSHubsApi (String uriStr, WebSocketEventHandler webSocketEventHandler) throws URISyntaxException {
        wsClient = new WSConnection(uriStr);
        wsClient.setEventHandler(webSocketEventHandler);
        wsClient.connect();
    }

    public boolean isConnected(){return wsClient.isConnected();}

    private FunctionResult __constructMessage (String hubName, String functionName, JSONArray argsArray) throws JSONException{
        int messageId= wsClient.getNewMessageId();
        JSONObject msgObj = new JSONObject();
        msgObj.put("hub",hubName);
        msgObj.put("function",functionName);
        msgObj.put("args", argsArray);
        msgObj.put("ID", messageId);
        wsClient.send(msgObj.toJSONString());
        return new FunctionResult(wsClient,messageId);
    }

    private static <TYPE_ARG> void __addArg(JSONArray argsArray, TYPE_ARG arg) throws JSONException {
        try {
            argsArray.add(arg);
        } catch (Exception e) {
            JSONArray aux = new JSONArray();
            aux.add(gson.toJson(arg));
            argsArray.add(aux);
        }
    }
    
    public class SyncHub {
        private class Server {
            public static final String HUB_NAME = "SyncHub";
            
            public <TYPE_A> FunctionResult phoneNumbers (TYPE_A phoneNumberArray) throws JSONException{
                JSONArray argsArray = new JSONArray();
                __addArg(argsArray,phoneNumberArray);
                return __constructMessage(HUB_NAME, "phoneNumbers",argsArray);
            }
        }
        public Server server = new Server();
        public Client_SyncHub client = new Client_SyncHub();
    }
    public class TaskHub {
        private class Server {
            public static final String HUB_NAME = "TaskHub";
            
            public <TYPE_A, TYPE_B, TYPE_C, TYPE_D> FunctionResult addTask (TYPE_A body, TYPE_B creatorId, TYPE_C receiverId, TYPE_D createdTime) throws JSONException{
                JSONArray argsArray = new JSONArray();
                __addArg(argsArray,body);
				__addArg(argsArray,creatorId);
				__addArg(argsArray,receiverId);
				__addArg(argsArray,createdTime);
                return __constructMessage(HUB_NAME, "addTask",argsArray);
            }
        }
        public Server server = new Server();
        public Client_TaskHub client = new Client_TaskHub();
    }
    public class Places {
        private class Server {
            public static final String HUB_NAME = "Places";
            
            public <TYPE_A, TYPE_B, TYPE_C, TYPE_D, TYPE_E> FunctionResult createPlace (TYPE_A name, TYPE_B userId, TYPE_C icon, TYPE_D createdTime, TYPE_E type) throws JSONException{
                JSONArray argsArray = new JSONArray();
                __addArg(argsArray,name);
				__addArg(argsArray,userId);
				__addArg(argsArray,icon);
				__addArg(argsArray,createdTime);
				__addArg(argsArray,type);
                return __constructMessage(HUB_NAME, "createPlace",argsArray);
            }

            public <TYPE_A, TYPE_B, TYPE_C, TYPE_D, TYPE_E, TYPE_F> FunctionResult updatePlace (TYPE_A id, TYPE_B name, TYPE_C userId, TYPE_D icon, TYPE_E createdTime, TYPE_F type) throws JSONException{
                JSONArray argsArray = new JSONArray();
                __addArg(argsArray,id);
				__addArg(argsArray,name);
				__addArg(argsArray,userId);
				__addArg(argsArray,icon);
				__addArg(argsArray,createdTime);
				__addArg(argsArray,type);
                return __constructMessage(HUB_NAME, "updatePlace",argsArray);
            }
        }
        public Server server = new Server();
        public Client_Places client = new Client_Places();
    }
    public class ChatHub {
        private class Server {
            public static final String HUB_NAME = "ChatHub";
            
            public <TYPE_A> FunctionResult sendToAll (TYPE_A message) throws JSONException{
                JSONArray argsArray = new JSONArray();
                __addArg(argsArray,message);
                return __constructMessage(HUB_NAME, "sendToAll",argsArray);
            }
        }
        public Server server = new Server();
        public Client_ChatHub client = new Client_ChatHub();
    }
    public class LoggingHub {
        private class Server {
            public static final String HUB_NAME = "LoggingHub";
            
            public <TYPE_A, TYPE_B, TYPE_C, TYPE_D> FunctionResult logIn (TYPE_A phoneNumber, TYPE_B gcmId, TYPE_C name, TYPE_D email) throws JSONException{
                JSONArray argsArray = new JSONArray();
                __addArg(argsArray,phoneNumber);
				__addArg(argsArray,gcmId);
				__addArg(argsArray,name);
				__addArg(argsArray,email);
                return __constructMessage(HUB_NAME, "logIn",argsArray);
            }
        }
        public Server server = new Server();
        public Client_LoggingHub client = new Client_LoggingHub();
    }
    public class PlaceConfigHub {
        private class Server {
            public static final String HUB_NAME = "PlaceConfigHub";
            
            public <TYPE_A> FunctionResult createPlace (TYPE_A place) throws JSONException{
                JSONArray argsArray = new JSONArray();
                __addArg(argsArray,place);
                return __constructMessage(HUB_NAME, "createPlace",argsArray);
            }

            public <TYPE_A> FunctionResult editPlace (TYPE_A place) throws JSONException{
                JSONArray argsArray = new JSONArray();
                __addArg(argsArray,place);
                return __constructMessage(HUB_NAME, "editPlace",argsArray);
            }
        }
        public Server server = new Server();
        public Client_PlaceConfigHub client = new Client_PlaceConfigHub();
    }
}
    