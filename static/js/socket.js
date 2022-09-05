$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://196.64.19.187', {transports: ['websocket']});
    //receive details from server
    socket.on('response', function(msg){
        console.log("Received number" + msg.data);
        $('#log').html(msg.data);
	$('#logesp').html(msg.esp);
    });

});