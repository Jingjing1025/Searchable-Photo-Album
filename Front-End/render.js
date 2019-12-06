var apigClient = apigClientFactory.newClient({
    accessKey: '',
    secretKey: ''
});
var albumBucketName = "b2homework3";
var bucketRegion = "us-east-1";
var albumName = "myAlbum";

AWS.config.update({
  region: bucketRegion,
  credentials: new AWS.CognitoIdentityCredentials({
    IdentityPoolId: ""
  })
});

// var s3 = new AWS.S3({
//   apiVersion: "2006-03-01",
//   params: { Bucket: albumBucketName }
// });



document.getElementById("displaytext").style.display = "none";

function searchPhoto()
{
    var user_message = document.getElementById('note-textarea').value;

    var body = { "q": user_message };
    var params = {};
    var additionalParams = {};

    apigClient.photoPost(params, body , additionalParams).then(function(res){
        var data = {}
        var data_array = []
        resp_data  = res["data"]["photos_result"]
        alert(resp_data)
        resp_data.forEach(function(obj) {var json = {};
                  json["bannerImg1"] = "https://b2homework3.s3.amazonaws.com/"+obj;
                 data_array.push(json) }
                );

        data["images"] = data_array;
        console.log(data);

        data.images.forEach( function(obj) {
            var img = new Image();
            img.src = obj.bannerImg1;
            img.setAttribute("class", "banner-img");
            img.setAttribute("alt", "effy");
            document.getElementById("img-container").appendChild(img);
            document.getElementById("displaytext").style.display = "block";
          });
      }).catch( function(result){});

}

function uploadPhoto() {
  var files = document.getElementById("file_path").files;
  if (!files.length) {
    return alert("Please choose a file to upload first.");
  }
  var file = files[0];
  var fileName = file.name;
  var albumPhotosKey = encodeURIComponent(fileName);
  var photoKey = fileName;
  // Use S3 ManagedUpload class as it supports multipart uploads
  var upload = new AWS.S3.ManagedUpload({
    params: {
      Bucket: albumBucketName,
      Key: photoKey,
      Body: file,
      ACL: "public-read"
    }
  });

  var promise = upload.promise();

  promise.then(
    function(data) {
      alert("Successfully uploaded photo.");
    },
    function(err) {
      console.log(err.message)
      return alert("There was an error uploading your photo: ", err.message);
    }
  );
}