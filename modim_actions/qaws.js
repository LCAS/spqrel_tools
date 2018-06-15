// log display function
function append(text) {
  // document.getElementById("websocket_events").insertAdjacentHTML('beforeend', "<li>" + text + ";</li>");
  console.log(text);
} 

// websocket global variable
var websocket = null;

function wsrobot_connected() {
  var connected = false;
  if (websocket!=null)
    console.log("websocket.readyState: "+websocket.readyState)
  if (websocket!=null && websocket.readyState==1) {
    connected = true;
  }
  console.log("connected: "+connected)
  return connected;
}

function wsrobot_init(ip, port) {
    var url = "ws://"+ip+":"+port+"/modimwebsocketserver";
    console.log(url);
    websocket = new WebSocket(url);

    websocket.onmessage = function(event){
	console.log("message received: "+event.data);
	v = event.data.split('_');
	
	if (v[0]=='display') {
            if (v[1]=='text')
		document.getElementById(v[1]+'_'+v[2]).innerHTML = v[3];
            else if (v[1]=='image'){
		p = v[3];
		for (i=4; i<v.length; i++){
		    p = p + "_" + v[i];
		}

		console.log("image: " + p);

		
		document.getElementById(v[1]+'_'+v[2]).src = p;
	    }
	    else if (v[1]=='button') {
		var b = document.createElement("input");
		//Assign different attributes to the element. 
		p = v[2] 
		for (i=3; i<v.length; i++){
		    p = p + "_" + v[i];
		}
		console.log(p);
		vp = p.split('$');

		if (vp[1].substr(0,3)=='img') {
                    b.type = "image";
                    b.src = vp[1];
		}
		else {
                    b.type = "button";
                    b.value = vp[1]; 
		}
		
		b.name = vp[0]; 
		b.id = vp[0];
		b.onclick = function(event) { button_fn(event) };
		var bdiv = document.getElementById("buttons");
		bdiv.appendChild(b);
            }
        }
        else if (v[0]=='remove') {
            if (v[1]=='buttons') {
                var bdiv = document.getElementById("buttons");
                var fc = bdiv.firstChild;
                while( fc ) {
                    bdiv.removeChild( fc );
                    fc = bdiv.firstChild;
                }

            }
        }
        else if (v[0]=='url') {
            console.log('load url: '+v[1])
            window.location.assign(v[1])
        }
    } 

    websocket.onopen = function(){
      append("connection received");
      document.getElementById("status").innerHTML = "<font color='green'>OK</font>";

    } 

    websocket.onclose = function(){
      append("connection closed");
      document.getElementById("status").innerHTML = "<font color='red'>NOT CONNECTED</font>";
    }

    websocket.onerror = function(){
      append("!!!connection error!!!");
    }

}
 
function wsrobot_quit() {
    websocket.close();
    websocket = null;
}

function wsrobot_send(data) {
  if (websocket!=null)
    websocket.send(data);
}


function button_fn(event) {
  var bsrc = event.srcElement || event.originalTarget
  console.log('websocket button '+bsrc.id)
  wsrobot_send(bsrc.id);
}


