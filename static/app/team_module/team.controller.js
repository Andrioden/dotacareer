app.controller('TeamController', function ($rootScope, $scope, $http, $modal, WebSocketService) {

    // LISTEN TO EVENTS // EXPOSE METHODS TO OTHER CONTROLLERS
    WebSocketService.subscribe("NewTeamApplication", function(newTeamApplication){
        $rootScope.player.team.applications.push(newTeamApplication);
        $rootScope.$apply();
    });

    // EXPOSED ACTIONS FOR HTML
    $scope.openCreateTeamDialog = function () {

        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'createTeamDialog.html',
            controller: 'CreateTeamDialogController',
        });

        modalInstance.result.then(
            // Dialog successfully closed
            function (team_name) {
               createTeam(team_name);
            // Canceled
            }, function () {}
        );

    };

    $scope.openApplyTeamDialog = function() {
        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'applyTeamDialog.html',
            controller: 'ApplyTeamDialogController',
        });

        modalInstance.result.then(
            // Dialog successfully closed
            function (data_from_dialog) {
                applyToTeam(data_from_dialog);
            // Canceled
            }, function () {}
        );
    }

    $scope.acceptApplication = function(application) {
        $http.post('/api/teams/acceptApplication', {application_id: application.id}).
            then(function(response) {
                deleteApplication(application.id);
                $rootScope.player.team.members.push(application.player);
            }, function(response) {
                AlertError(response);
            });
    }

    $scope.declineApplication = function(application) {
        $http.post('/api/teams/declineApplication', {application_id: application.id}).
            then(function(response) {
                deleteApplication(application.id);
            }, function(response) {
                AlertError(response);
            });
    }

    $scope.kickMember = function(member) {
        if (confirm("Are you sure you want to delete " + member.nick + "?")) {
            $http.post('/api/teams/kickMember', {player_id: member.id}).
                then(function(response) {
                    deleteMember(member.id);
                }, function(response) {
                    AlertError(response);
                });
        }
    }

    // INTERNAL FUNCTIONS
    function createTeam(team_name) {
        $http.post('/api/teams/register', {team_name: team_name}).
            then(function(response) {
                $rootScope.player.team = response.data.team;
            }, function(response) {
                AlertError(response);
            });
    }

    function applyToTeam(api_data) {
        $http.post('/api/teams/sendApplication', api_data).
            then(function(response) {
                console.log(response)
            }, function(response) {
                AlertError(response);
            });
    }

    function deleteApplication(application_id) {
        for(var i=0; i<$scope.player.team.applications.length; i++) {
            if ($scope.player.team.applications[i].id == application_id)
                $scope.player.team.applications.splice(i,1);
        }
    }

    function deleteMember(member_id) {
        for(var i=0; i<$scope.player.team.members.length; i++) {
            if ($scope.player.team.members[i].id == member_id)
                $scope.player.team.members.splice(i,1);
        }
    }

});

app.controller('CreateTeamDialogController', function ($scope, $modalInstance) {
    $scope.ok = function () {
        $modalInstance.close($scope.team_name);
    };
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
});

app.controller('ApplyTeamDialogController', function ($scope, $modalInstance, $http) {
    // IMPORTANT CONTROLLER VARIABLES
    $scope.teams = undefined;

    // CONSTRUCTOR
    $http.get('/api/teams/all').
        then(function(response) {
            $scope.teams = response.data;
        }, function(response) {
            AlertError(response);
        });

    // STANDARD DIALOG AND OTHER EXPOSED FUNCTIONS
    $scope.ok = function () {
        $modalInstance.close({ // return data to dialog opener
            team_id: $scope.team_id,
            text: $scope.application_text
        });
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

});