//
// Data constructs and initialization.
//

// **DO THIS**:
//   Replace BUCKET_NAME with the bucket name.
//
var BucketName = 'smart-social-distancing-test';

// **DO THIS**:
//   Replace this block of code with the sample code located at:
//   Cognito -- Manage Identity Pools -- [identity_pool_name] -- Sample Code -- JavaScript
//
// Initialize the Amazon Cognito credentials provider
AWS.config.region = 'ap-northeast-2'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'ap-northeast-2:04866291-7732-48d6-8432-17598871880b',
});

// Create a new service object
var s3 = new AWS.S3({
  apiVersion: '2006-03-01',
  params: {Bucket: BucketName}
});

// A utility function to create HTML.
function getHtml(template) {
  return template.join('\n');
}


//
// Functions
//

// List the photo albums that exist in the bucket.
function listfiles() {
  s3.listObjects({Delimiter: '/'}, function(err, data) {
    if (err) {
      return alert('There was an error listing your bucket: ' + err.message);
    } else {
      var files = data.CommonPrefixes.map(function(commonPrefix) {
        var prefix = commonPrefix.Prefix;
        var albumName = decodeURIComponent(prefix.replace('/', ''));
        return getHtml([
          '<li>',
            '<button style="margin:5px;" onclick="viewcsv(\'' + albumName + '\')">',
              albumName,
            '</button>',
          '</li>'
        ]);
      });
      var message = files.length ?
        getHtml([
          '<p>Click on an file name to view it.</p>',
        ]) :
        '<p>You do not have any csv file. Please upload csv file.';
      var htmlTemplate = [
        '<h2>csv file</h2>',
        message,
        '<ul>',
          getHtml(files),
        '</ul>',
      ]
      document.getElementById('viewer').innerHTML = getHtml(htmlTemplate);
    }
  });
}

// Show the photos that exist in an album.
function viewcsv(filename) {
  var csvfileKey = encodeURIComponent(filename) + '/';
  s3.listObjects({Prefix: csvfileKey}, function(err, data) {
    if (err) {
      return alert('There was an error viewing your bucket: ' + err.message);
    }
    // 'this' references the AWS.Request instance that represents the response
    var href = this.request.httpRequest.endpoint.href;
    var bucketUrl = href + BucketName + '/';

    var photos = data.Contents.map(function(file) {
      var photoKey = file.Key;
      var photoUrl = bucketUrl + encodeURIComponent(photoKey);
      return getHtml([
        '<span>',
          '<div>',
            '<br/>',
            photoUrl,
          '</div>',
          '<div>',
            '<span>',
              photoKey.replace(csvfileKey, ''),
            '</span>',
          '</div>',
        '</span>',
      ]);
    });
    var message = photos.length ?
      '<p>The following photos are present.</p>' :
      '<p>There are no photos in this album.</p>';
    var htmlTemplate = [
      '<div>',
        '<button onclick="listfiles()">',
          'Back To Albums',
        '</button>',
      '</div>',
      '<h2>',
        'Album: ' + filename,
      '</h2>',
      message,
      '<div>',
        getHtml(photos),
      '</div>',
      '<div>',
        '<button onclick="listfiles()">',
          'Back To Albums',
        '</button>',
      '</div>',
    ]
    document.getElementById('viewer').innerHTML = getHtml(htmlTemplate);
    document.getElementsByTagName('img')[0].setAttribute('style', 'display:none;');
  });
}

