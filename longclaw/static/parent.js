$('.menu .item')
    .tab();
$('.ui.dropdown')
    .dropdown();

function login() {
    //  alert("hello");
    console.log(45);
}
$('.infinite.example.demo.segment')
    .visibility({
        once: false,
        // update size when new content loads
        observeChanges: true,
        // load content on bottom edge visible
        onBottomVisible: function() {
            // loads a max of 5 times
            window.loadFakeContent();
        }
    });
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

var knuth = angular.module("knuth", ['ngCookies', 'ngFileUpload']);
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
]  );
