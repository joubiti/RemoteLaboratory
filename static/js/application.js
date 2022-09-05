$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://196.64.19.187');
    //receive details from server

    socket.on('redirect', function (data){
    window.location = data.url;
    socket.disconnect(); 
});

    socket.on('timeleft', function(msg){
    console.log("Received number" +msg.data);
    $('#log').html(msg.data);
    

});


});