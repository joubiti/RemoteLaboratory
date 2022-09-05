$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://196.64.19.187', {transports: ['websocket']});
    //receive details from server
    socket.on('timeesp', function(msg){
        console.log("Received number" + msg.data);
        $('#log').html(msg.data);
    });

    socket.on('redirectesp', function (data){
    window.location = data.url;
    socket.disconnect(); 
});


});