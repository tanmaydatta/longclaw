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

$(document).ready(function() { /*code here*/
    var elements = $('#main_menu').children();
    elements.each(function(index, element) {
        $(this).css({
            "width": (100 / elements.length) + "%",
        });
    });
});

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
