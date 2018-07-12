function test(name){
    alert(name);
}

var demoIO = io('/demo');

demoIO.on('update', function(data){
    alert(data)
});
