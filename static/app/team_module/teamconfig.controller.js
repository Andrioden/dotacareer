app.controller('TeamConfigDialogController', function ($rootScope, $scope, $modalInstance, $http, $timeout) {

    // CONSTRUCTOR
    $scope.rankedTime = $rootScope.player.team.ranked_time;
    if (!$scope.rankedTime.timezoneAdjusted) {
        $scope.rankedTime.start_hour -= getTimezoneOffsetHours();
        $scope.rankedTime.end_hour -= getTimezoneOffsetHours();
        $scope.rankedTime.timezoneAdjusted = true;
    }
    // Timeout needed to redraw the slider because of limitations of the slider plugin (https://github.com/rzajac/angularjs-slider/issues/79)
    $timeout(function () {
        $scope.$broadcast('rzSliderForceRender');
    });

    if (!hasFullMembersData()) loadFullMembersData();


    // STANDARD DIALOG AND OTHER EXPOSED FUNCTIONS
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.isDoingConfigAction = false;

    $scope.update = function () {
        $scope.isDoingConfigAction = true;
        $http.post('/api/teams/updateConfig', {
            ranked_start_hour: $scope.rankedTime.start_hour + getTimezoneOffsetHours(),
            ranked_end_hour: $scope.rankedTime.end_hour + getTimezoneOffsetHours()
        })
            .then(function(response) {
                $scope.isDoingConfigAction = false;
            }, function(response) {
                $scope.isDoingConfigAction = false;
                alertError(response);
            });
    };

    $scope.translateHoursToPrettyHours = function(value) {
        return value + ":00"
    }

    // PRIVATE FUNCTIONS

    function getTimezoneOffsetHours() {
        return (new Date()).getTimezoneOffset() / 60;
    }

    function hasFullMembersData() {
        return $rootScope.player.team.members[0].stats != undefined;
    }

    function loadFullMembersData() {
        $http.get('/api/teams/fullMembersData').
            then(function(response) {
                $rootScope.player.team.members = response.data;
            }, function(response) {
                alertError(response);
            });
    }

});