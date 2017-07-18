var hostname = location.hostname;
console.log(hostname);


function send(data) {
  var buffer=JSON.stringify(data);
  socket.send(buffer);
}

function init() {
  var host_name = window.location.hostname;
  socket = new WebSocket("ws://" + host_name + ":8128");
  socket.binaryType = "arraybuffer";

  socket.onopen = function () {
    console.log("Connected!");
  };

  socket.onmessage = function (e) {
    if (typeof e.data == "string") {
      console.log("Text message received: " + e.data);
      var payload = JSON.parse(e.data);
      console.log("payload= " + JSON.stringify(payload, null, 2));

    } else {
      var arr = new Uint8Array(e.data);
      var hex = '';
      for (var i = 0; i < arr.length; i++) {
        hex += ('00' + arr[i].toString(16)).substr(-2);
      }
      console.log("Binary message received: " + hex);
    }
  };

  socket.onclose = function (e) {
    socket = null;
    console.log("Connection closed. Reason: " + e.reason);
  };

}
