package servlets;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;

import javax.servlet.ServletConfig;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.http.HttpEntity;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.protocol.HTTP;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONObject;



/**
 * Servlet implementation class TwitterProvider
 */
@WebServlet("/*")
public class TwitterProvider extends HttpServlet {
	private static final long serialVersionUID = 1L;
	private static CloseableHttpClient client = HttpClients.createDefault();
	
    private static String sourceURL = "http://130.56.255.77:5984/australia";
    private static String resultURL = "http://130.56.255.77:5984/result";
//    private static String deepURL = "http://130.56.255.77:5984/deep";
    private static ArrayList<String> functions = new ArrayList<>();
    
    private static HashMap<String, Integer> counterandsize = new HashMap<String, Integer>();
    
    /**
     * @see HttpServlet#HttpServlet()
     */
    public TwitterProvider() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see Servlet#init(ServletConfig)
	 */
	public void init(ServletConfig config) throws ServletException {
		functions.add("emotion");
		functions.add("topic");
		functions.add("melbourne");
		functions.add("sydney");
		functions.add("perth");
		functions.add("adelaide");
		functions.add("brisbane");
		functions.add("australia");
//		functions.add("racism");
		
		for(String target:functions){
			counterandsize.put(target+"counter", 0);
			counterandsize.put(target+"size", 1000);
		}
	}

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String path = request.getPathInfo();
		if(path == null){
			response.getWriter().append("welcome");
		}else{
			String[] pathDetail = path.split("/");
			switch (pathDetail[1]) {
			case "instruction":
				response.getWriter().append("ADDRESS=ec2-13-55-33-247.ap-southeast-2.compute.amazonaws.com:8080\n");
				response.getWriter().append("root: http://ADDRESS/cloud\n");
				response.getWriter().append("state: http://ADDRESS/cloud/state\n");
				response.getWriter().append("instruction: http://ADDRESS/cloud/instruction\n\n");
				response.getWriter().append("GET section:\n");
				response.getWriter().append("get for emotion or topic: http://ADDRESS/cloud/twitter/(emotion or topic)\n    format:[{\"id\"=(id String),\"key\"=(id String),\"value\"=(text String)}]\n");
				response.getWriter().append("get for hot topic by location: http://ADDRESS/cloud/twitter/(location in lower case)\n    format:[{\"id\"=(id String),\"key\"=(id String),\"value\"=(text String)}]\n");
				response.getWriter().append("get for result: http://ADDRESS/cloud/result/(name)/level=(number)\n");
				response.getWriter().append("get for hot topic result: http://ADDRESS/cloud/hottopic/(location in lowercase)\n");
				response.getWriter().append("get for setting parameters:\n");
				response.getWriter().append("    set counter: http://ADDRESS/cloud/setting/(function)/(functioncounter)=(number)\n");
				response.getWriter().append("    set size: http://ADDRESS/cloud/setting/(function)/(functionsize)=(number)\n");
				response.getWriter().append("    set source DB address: http://ADDRESS/cloud/setting/source/(address:port)=(DB name)\n");
				response.getWriter().append("    set result DB address: http://ADDRESS/cloud/setting/result/(address:port)=(DB name)\n");
//				response.getWriter().append("    set deep DB address: http://ADDRESS/cloud/setting/deep/(address:port)=(DB name)\n");
				response.getWriter().append("get for add function: http://ADDRESS/cloud/addfunction/(function name)\n");
				response.getWriter().append("get for delete function: http://ADDRESS/cloud/deletefunction/(function name)\n\n");
				response.getWriter().append("POST section:\n");
				response.getWriter().append("post for emotion or topic: http://ADDRESS/cloud/result/(emotion or topic)\n    format: [{\"id\"=(id String),\"(emotion or topic)\"=(emotion String)}]\n");
				response.getWriter().append("post for topic by location: http://ADDRESS/cloud/location/(location in lower case)\n    format: {(word1 String)=(count int)}\n");
				break;
			case "twitter":
				if(functions.contains(pathDetail[2])){
					JSONArray rest = new JSONArray();
					synchronized (counterandsize) {
						rest = this.getTwitters(pathDetail[2], counterandsize.get(pathDetail[2]+"counter"), counterandsize.get(pathDetail[2]+"size"));
						counterandsize.put(pathDetail[2]+"counter", counterandsize.get(pathDetail[2]+"counter")+rest.length());
					}
					response.getWriter().append(rest.toString());
				}else{
					response.getWriter().append("invalid address");
				}
				break;
//			case "deep":
//				response.getWriter().append(this.getJSON(deepURL+"/"+pathDetail[2]).getJSONArray("tweets").toString());
//				break;
			case "result":
				String[] levelDetail = pathDetail[3].split("=");
				response.getWriter().append(this.getResult(pathDetail[2], levelDetail[1]).toString());
				break;
			case "hottopic":
				response.getWriter().append(this.getJSON(resultURL+"/"+pathDetail[2]).toString());
				break;
			case "setting":
				String[] settingsDetail = pathDetail[3].split("=");
				if(functions.contains(pathDetail[2])){
					counterandsize.put(settingsDetail[0], Integer.parseInt(settingsDetail[1]));
					response.getWriter().append("modify success\n");
					response.getWriter().append("now "+settingsDetail[0]+" = "+counterandsize.get(settingsDetail[0]));
				}else if(pathDetail[2].equals("source")){
					sourceURL = "http://"+settingsDetail[0]+"/"+settingsDetail[1];
					response.getWriter().append("modify sucess\n");
					response.getWriter().append("now sourceURL = "+sourceURL);
				}else if(pathDetail[2].equals("result")){
					resultURL = "http://"+settingsDetail[0]+"/"+settingsDetail[1];
					response.getWriter().append("modify sucess\n");
					response.getWriter().append("now resultURL = "+resultURL);
//				}else if(pathDetail[2].equals("deep")){
//					deepURL = "http://"+settingsDetail[0]+"/"+settingsDetail[1];
//					response.getWriter().append("modify success\n");
//					response.getWriter().append("now deepURL = "+deepURL);
				}else{
					response.getWriter().append("no such parameter");
				}
				break;
			case "addfunction":
				functions.add(pathDetail[2]);
				counterandsize.put(pathDetail[2]+"counter", 0);
				counterandsize.put(pathDetail[2]+"size", 1000);
				response.getWriter().append("add function success\n");
				response.getWriter().append("now functions are: "+functions.toString());
				break;
			case "deletefunction":
				functions.remove(pathDetail[2]);
				counterandsize.remove(pathDetail[2]+"counter");
				counterandsize.remove(pathDetail[2]+"size");
				response.getWriter().append("delete function success\n");
				response.getWriter().append("now functions are: "+functions.toString());
				break;
			case "state":
				response.getWriter().append("source DB address: "+sourceURL+"\n");
				response.getWriter().append("source DB state:\n");
				response.getWriter().append(this.getJSON(sourceURL).toString()+"\n");
				response.getWriter().append("result DB address: "+resultURL+"\n");
				response.getWriter().append("result DB state:\n");
				response.getWriter().append(this.getJSON(resultURL).toString()+"\n");
//				response.getWriter().append("deep DB address: "+resultURL+"\n");
//				response.getWriter().append("deep DB state:\n");
//				response.getWriter().append(this.getJSON(deepURL).toString()+"\n");
				response.getWriter().append("Server state:\n");
				response.getWriter().append("functions are: "+functions.toString()+"\n");
				response.getWriter().append("parameters state:\n");
				for(String target:functions){
					response.getWriter().append(target+"counter = "+counterandsize.get(target+"counter")+"\n");
					response.getWriter().append(target+"size = "+counterandsize.get(target+"size")+"\n");
				}
				break;
			default:
				response.getWriter().append("invalid address");
				break;
			}
		}
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String path = request.getPathInfo();
		if(path == null){
			response.getWriter().append("invalid upload address");
		}else{
			String[] pathDetail = path.split("/");
			switch (pathDetail[1]) {
			case "result":
				if(functions.contains(pathDetail[2])){
					BufferedReader input = new BufferedReader(new InputStreamReader(request.getInputStream()));
					String inputString = input.readLine();
					JSONArray inputJSONArray = new JSONArray(inputString);
//					response.getWriter().append("success");
					for(int i=0;i<inputJSONArray.length();i++){
						JSONObject inputJSON = inputJSONArray.getJSONObject(i);
						String id = inputJSON.getString("id");
						String result = inputJSON.getString(pathDetail[2]);
						this.postTwitters(pathDetail[2], id, result);
					}
					synchronized(counterandsize){
						counterandsize.put(pathDetail[2]+"counter", 0);
					}
					response.getWriter().append("success");
				}else{
					response.getWriter().append("invalid upload address");
				}
				break;
			case "location":
				if(functions.contains(pathDetail[2])){
					BufferedReader input = new BufferedReader(new InputStreamReader(request.getInputStream()));
					String inputString = input.readLine();
					JSONObject inputJSON = new JSONObject(inputString);
					this.postResult(pathDetail[2], inputJSON);
					response.getWriter().append("success");
				}else{
					response.getWriter().append("invalid upload address");
				}
				break;
			default:
				response.getWriter().append("invalid upload address");
				break;
			}
		}
	}
	
	private JSONObject getJSON(String url){
		JSONObject result = null;
		HttpGet get = new HttpGet(url);
		try {
			CloseableHttpResponse response = client.execute(get);
			try{
				HttpEntity entity = response.getEntity();
				result = new JSONObject(EntityUtils.toString(entity));
				EntityUtils.consume(entity);
			}finally {
				response.close();
			}			
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return result;
	}
	
	private JSONObject postJSON(String url, JSONObject content){
		JSONObject result = null;
		HttpPost post = new HttpPost(url);
		post.addHeader(HTTP.CONTENT_TYPE, "application/json");
		try {
			post.setEntity(new StringEntity(content.toString()));
			CloseableHttpResponse response = client.execute(post);
			try{
				HttpEntity entity = response.getEntity();
				result = new JSONObject(EntityUtils.toString(entity));
				EntityUtils.consume(entity);
			}finally {
				response.close();
			}
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (UnsupportedEncodingException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return result;
	}
	
	private JSONArray getTwitters(String target, int skip, int limit){
		return this.getJSON(sourceURL+"/_design/master/_view/"+target+"?skip="+skip+"&limit="+limit).getJSONArray("rows");
		//"key":(_id)
	}
	
	private synchronized void postTwitters(String target, String id, String result){
		JSONObject previousJSON = this.getJSON(sourceURL+"/"+id);
		previousJSON.put(target, result);
		this.postJSON(sourceURL, previousJSON);
		//Additional to do
	}
	
	private synchronized void postResult(String location, JSONObject input){
		JSONObject previousJSON = this.getJSON(resultURL+"/"+location);
		Iterator iterator = input.keys();
		while(iterator.hasNext()){
			String key = (String) iterator.next();
			int value = input.getInt(key);
			if(previousJSON.has(key)){
				previousJSON.put(key, value+previousJSON.getInt(key));
			}else{
				previousJSON.put(key, value);
			}
		}
		this.postJSON(resultURL, previousJSON);
	}
	
	private JSONObject getResult(String target, String level){
		return this.getJSON(sourceURL+"/_design/master/_view/"+target+"?group_level="+level);
	}
}
