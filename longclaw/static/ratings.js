$('#ratings').addClass("active item");
$('table').tablesort();


var myApp = angular.module('myApp', ['angularUtils.directives.dirPagination']);
myApp.controller('MyController', MyController);

function MyController($scope) {

  $scope.currentPage = 1;
  $scope.pageSize = 10;
  $scope.meals = [];

  var dishes = [
    'noodles',
    'sausage',
    'beans on toast',
    'cheeseburger',
    'battered mars bar',
    'crisp butty',
    'yorkshire pudding',
    'wiener schnitzel',
    'sauerkraut mit ei',
    'salad',
    'onion soup',
    'bak choi',
    'avacado maki'
  ];
  var sides = [
    'with chips',
    'a la king',
    'drizzled with cheese sauce',
    'with a side salad',
    'on toast',
    'with ketchup',
    'on a bed of cabbage',
    'wrapped in streaky bacon',
    'on a stick with cheese',
    'in pitta bread'
  ];
  for (var i = 1; i <= 100; i++) {
    var dish = dishes[Math.floor(Math.random() * dishes.length)];
    var side = sides[Math.floor(Math.random() * sides.length)];
    $scope.meals.push('meal ' + i + ': ' + dish + ' ' + side);
  }
}

function OtherController($scope) {
  
  $scope.pageChangeHandler = function(num) {
      console.log('meals page changed to ' + num);
  };
}

function MyController2($scope) {

  $scope.currentPage = 1;
  $scope.pageSize = 10;
  $scope.meals = [];

  var dishes = [
    'noodles',
    'sausage',
    'beans on toast',
    'cheeseburger',
    'battered mars bar',
    'crisp butty',
    'yorkshire pudding',
    'wiener schnitzel',
    'sauerkraut mit ei',
    'salad',
    'onion soup',
    'bak choi',
    'avacado maki'
  ];
  var sides = [
    'with chips',
    'a la king',
    'drizzled with cheese sauce',
    'with a side salad',
    'on toast',
    'with ketchup',
    'on a bed of cabbage',
    'wrapped in streaky bacon',
    'on a stick with cheese',
    'in pitta bread'
  ];
  for (var i = 1; i <= 100; i++) {
    var dish = dishes[Math.floor(Math.random() * dishes.length)];
    var side = sides[Math.floor(Math.random() * sides.length)];
    $scope.meals.push('meal ' + i + ': ' + dish + ' ' + side);
  }
}

function OtherController($scope) {
  
  $scope.pageChangeHandler = function(num) {
      console.log('meals page changed to ' + num);
  };
}



// $(document).ready(function() { 
//     $("table") 
//     .tablesorter({widthFixed: true, widgets: ['zebra']}) 
//     .tablesorterPager({container: $("#pager")}); 
// }); 

// /*global m, Pagination, window*/
// // angular js:
// 'use strict';
// (function(m, Pagination) {
//     // alert("working");
//     var array = [],
//         i,
//         module = {};

//     for (i = 0; i < 100; i += 1) {
//         array.push({
//             id: i,
//             name: 'name ' + i
//         });
//     }

//     function list(data) {
//         return m('.ui.segment.sixteen.wide.column', [
//             m('ul.ui.bulleted.list', data.map(function(item) {
//                 return m('li', {
//                     key: item.id
//                 }, item.name);
//             }))
//         ]);
//     }

//     function table(data) {
//         return m('.ui.sixteen.wide.column', [
//             m('table.ui.table', [
//                 m('tbody', data.map(function(item) {
//                     return m('tr', {
//                         key: item.id
//                     }, [
//                         m('td', item.id),
//                         m('td', item.name)
//                     ]);
//                 }))
//             ])
//         ]);
//     }

//     module.controller = function() {
//         module.vm.init();
//         this.pagination = m.component(Pagination, {
//             data: module.vm.data,
//             rowsperpage: module.vm.rowsperpage,
//             pagerender: list,
//             wrapperclass: 'column'
//         });
//         this.paginationCtrl = new this.pagination.controller();
//     };

//     module.vm = {};
//     module.vm.init = function() {
//         this.data = array;
//         this.rowsperpage = 10;
//         this.page = m.prop(3);
//     };


//     module.view = function(ctrl) {
//         return m('.ui.grid.page.one.column', [
//             m('h1', 'Pagination'),
//             m.component(Pagination, {
//                 data: module.vm.data,
//                 rowsperpage: module.vm.rowsperpage,
//                 pagerender: list,
//                 wrapperclass: 'column',
//                 page: module.vm.page
//                     /*,
//                                     classes: {
//                                         leftIconClass: 'glyphicon glyphicon-arrow-left',
//                                         rightIconClass: 'glyphicon glyphicon-arrow-right'
//                                     }*/
//             }),
//             m.component(Pagination, {
//                 data: module.vm.data,
//                 rowsperpage: module.vm.rowsperpage,
//                 pagerender: table,
//                 wrapperclass: 'column',
//                 classes: {
//                     leftIconClass: 'left arrow icon',
//                     rightIconClass: 'right arrow icon'
//                 }
//             }),
//             m('.row', [
//                 m('.column', [
//                     m('br')
//                 ])
//             ]),
//             ctrl.pagination.view(ctrl.paginationCtrl),
//             m('.row', [
//                 m('.column', [
//                     m('button.ui.button', {
//                         onclick: function() {
//                             module.vm.data.splice(30, 10);
//                             ctrl.paginationCtrl.goToPage(4);
//                             module.vm.page(4);
//                         }
//                     }, 'go to page 3')
//                 ])
//             ])
//         ]);
//     };

//     m.mount(window.document.body, module);
// }(m, Pagination));
