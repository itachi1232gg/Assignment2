var express = require("express");
var app = express();
var request = require("request");

app.set("view engine","ejs");

app.get("/", function(req, res){
    var url = "http://ec2-13-55-33-247.ap-southeast-2.compute.amazonaws.com:8080/cloud/result/lte/value=3";
    request(url, function(error, response, body){
        if(!error && response.statusCode == 200) {
            var data = JSON.parse(body)
            
            res.render("aus", {data: data});
        }
    });
});


app.get("/au/ade", function(req, res){
    var url = "http://ec2-13-55-33-247.ap-southeast-2.compute.amazonaws.com:8080/cloud/result/lte/value=3";
    request(url, function(error, response, body){
        if(!error && response.statusCode == 200) {
            var data = JSON.parse(body)
            
            res.render("ade", {data: data});
        }
    });
});

app.get("/au/bri", function(req, res){
    var url = "http://ec2-13-55-33-247.ap-southeast-2.compute.amazonaws.com:8080/cloud/result/lte/value=3";
    request(url, function(error, response, body){
        if(!error && response.statusCode == 200) {
            var data = JSON.parse(body)
            
            res.render("bri", {data: data});
        }
    });
});

app.get("/au/mel", function(req, res){
    var url = "http://ec2-13-55-33-247.ap-southeast-2.compute.amazonaws.com:8080/cloud/result/lte/value=3";
    request(url, function(error, response, body){
        if(!error && response.statusCode == 200) {
            var data = JSON.parse(body)
            
            res.render("mel", {data: data});
        }
    });
});

app.get("/au/syd", function(req, res){
    var url = "http://ec2-13-55-33-247.ap-southeast-2.compute.amazonaws.com:8080/cloud/result/lte/value=3";
    request(url, function(error, response, body){
        if(!error && response.statusCode == 200) {
            var data = JSON.parse(body)
            
            res.render("syd", {data: data});
        }
    });
});

app.get("/au/per", function(req, res){
    var url = "http://ec2-13-55-33-247.ap-southeast-2.compute.amazonaws.com:8080/cloud/result/lte/value=3";
    request(url, function(error, response, body){
        if(!error && response.statusCode == 200) {
            var data = JSON.parse(body)
            
            res.render("per", {data: data});
        }
    });
});


app.listen(process.env.PORT, process.env.IP, function(){
    console.log("Result Display has started!!!");
});