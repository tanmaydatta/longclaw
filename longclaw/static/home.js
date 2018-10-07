
$('#home').addClass('active item');
$('.menu .item')
    .tab();
// $('.infinite.aa.demo.segment')
//     .visibility({
//         once: false,
//         // update size when new content loads
//         observeChanges: true,
//         // load content on bottom edge visible
//         onBottomVisible: function() {
//             // loads a max of 5 times
//             window.loadFakeContent();
//         }
//     });

$('.ui.sticky')
    .sticky({
        context: '#aa'
    });

var app = angular.module('knuth', []);
app.controller('ratingsCtrl', function($scope, $http) {
	var url="";
    $http.get(url)
    .then(function (response) {$scope.students = response.data.array;});
});
