var advertListApp = angular.module('advertListApp', []);

advertListApp.controller('AdvertListController', function AdvertListController($scope, $http) {
    $scope.adverts = [];
    $scope.tz_offset = new Date().getTimezoneOffset() * 60;

    $scope.get_adverts = function (page_number) {
        if (page_number < 0) {
            page_number = 0;
        }
        if (page_number > $scope.number_of_pages - 1) {
            page_number = $scope.number_of_pages - 1;
        }
        $http.get('https://25oy3abgv5.execute-api.eu-central-1.amazonaws.com/dev/adverts/get?page=' + page_number).then(function (response) {
            $scope.adverts = response.data.items;
            $scope.page = response.data.page;
            $scope.number_of_pages = response.data.number_of_pages;
            $scope.cnt = response.data.count;
            $scope.page_cnt = response.data.page_count;
            $scope.disable_prev = response.data.page === 0;
            $scope.disable_next = response.data.page === (response.data.number_of_pages - 1);
        })
    };

    $scope.range = function(min, max, step) {
        step = step || 1;
        var input = [];
        for (var i = min; i <= max; i += step) {
            input.push(i);
        }
        return input;
    };
});
