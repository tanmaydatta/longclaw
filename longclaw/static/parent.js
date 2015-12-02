$('#clear_menu')
    .sticky({
        context: '#stick_it'
    });
$('.menu .item')
    .tab();
$('.ui.dropdown')
    .dropdown();

function login() {
    //  alert("hello");
    console.log(45);
}

$('.paths.example .menu .item')
    .tab({
        context: '.paths.example'
    });
$('#context1 .menu .item')
    .tab({
        context: $('#context1')
    });
$('#context2 .menu .item')
    .tab({
        // special keyword works same as above
        context: 'parent'
    });

// $(document).ready(function() { /*code here*/
//     var elements = $('#main_menu').children();
//     elements.each(function(index, element) {
//         $(this).css({
//             "width": (100 / elements.length) + "%",
//         });
//     });
// });


// var app_id = "{{app_id}}";

var knuth = angular.module("knuth", ['ngCookies']);
knuth.controller("signout", ['$scope', '$cookies',
    function($scope, $cookies) {
        $scope.signout = function() {
            $cookies.remove('auth_key', {
                'path': '/'
            });
            location.reload();
        }
        // $scope.content="hello";
        // $scope.content = $scope.content + 'vvv';
    }
]);

// <script type="text/javascript">

knuth.controller("markdown", ['$scope',
    function($scope) {
        $scope.toHTML = function() {
            $('#m2html').text('');
            $('#m2html').append(markdown.toHTML($scope.content));
        }
        // $scope.content="hello";
        // $scope.content = $scope.content + 'vvv';
    }
]);
// </script>

knuth.controller('ratingsCtrl', function($scope, $http) {
    var url="http://knuth-jiit.me/all_ratings/";
    $http.get(url)
        .then(function(response) {
            $scope.students = response.data.users;
	    console.log($scope.students);
        });
});
