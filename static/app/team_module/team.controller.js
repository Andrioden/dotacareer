app.controller('TeamController', function ($rootScope, $scope, $http, $modal, WebSocketService) {

    // LISTEN TO EVENTS // EXPOSE METHODS TO OTHER CONTROLLERS
    WebSocketService.subscribe("Team_NewMember", function(player){
        // Adding the player to the current member list is done through the object path system
        deleteApplication(player.id);
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
               registerTeam(team_name);
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
                deleteApplication(application.player.id);
            }, function(response) {
                alertError(response);
            });
    }

    $scope.declineApplication = function(application) {
        $http.post('/api/teams/declineApplication', {application_id: application.id}).
            then(function(response) {
                deleteApplication(application.player.id);
            }, function(response) {
                alertError(response);
            });
    }

    $scope.kickMember = function(member) {
        if (confirm("Are you sure you want to kick " + member.nick + "?")) {
            $http.post('/api/teams/kickMember', {player_id: member.id}).
                then(function(response) {
                    deleteMember(member.id);
                }, function(response) {
                    alertError(response);
                });
        }
    }

    $scope.leaveTeam = function() {
        if (confirm("Are you sure you want to leave the team?")) {
            $http.post('/api/teams/leaveTeam').
                then(function(response) {
                    $scope.player.team = null;
                }, function(response) {
                    alertError(response);
                });
        }
    }

    $scope.openTeamConfigDialog = function() {
        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'teamConfigDialog.html',
            controller: 'TeamConfigDialogController',
            size: 'lg'
        });
    }

    // INTERNAL FUNCTIONS
    function registerTeam(team_name) {
        $http.post('/api/teams/register', {team_name: team_name}).
            then(function(response) {
                $rootScope.player.team = response.data.team;
            }, function(response) {
                alertError(response);
            });
    }

    function applyToTeam(api_data) {
        $http.post('/api/teams/sendApplication', api_data).
            then(function(response) {
                console.log(response)
            }, function(response) {
                alertError(response);
            });
    }

    function deleteApplication(playerId) {
        if (!$scope.player.team) return;
        for(var i=0; i<$scope.player.team.applications.length; i++) {
            if ($scope.player.team.applications[i].player.id == playerId)
                $scope.player.team.applications.splice(i,1);
        }
    }

    function deleteMember(playerId) {
        if (!$scope.player.team) return;
        for(var i=0; i<$scope.player.team.members.length; i++) {
            if ($scope.player.team.members[i].id == playerId)
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
    $http.get('/api/teams/rest/').
        then(function(response) {
            $scope.teams = response.data;
        }, function(response) {
            alertError(response);
        });

    // STANDARD DIALOG AND OTHER EXPOSED FUNCTIONS
    $scope.ok = function () {
        $modalInstance.close({ // return data to dialog opener
            team_id: $scope.teamId,
            text: $scope.applicationText
        });
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

});