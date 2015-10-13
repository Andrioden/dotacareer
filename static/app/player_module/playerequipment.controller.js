app.controller('PlayerEquipmentDialogController', function($rootScope, $scope, $modalInstance, $http){
    // IMPORTANT SCOPE VARIABLES
    $scope.shopEquipmentList;

    // CONSTRUCTOR
    $http.get('/api/players/shopEquipmentList', {cache: true}).
        then(function(response) {
            $scope.shopEquipmentList = response.data;
            updateEquipmentDataByOwnedEquipment();
        }, function(response) {
            alertError(response);
        });

    // LISTEN TO EVENTS // EXPOSE METHODS TO OTHER CONTROLLERS

    // STANDARD DIALOG AND OTHER EXPOSED FUNCTIONS
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.isEquipmentClicking = false;

    $scope.equipmentClick = function(equipment) {
        $scope.isEquipmentClicking = true;
        if (!equipment.owned) buy(equipment);
        else {
            if (equipment.isEquipped) setEquippedState(equipment, false)
            else setEquippedState(equipment, true)
        }
    }

    $scope.equipmentButtonClass = function(equipment) {
        if (equipment.owned) {
            if (equipment.isEquipped) return "btn-success";
            else return "btn-primary";
        }
        else return "btn-default"
    }

    // PRIVATE METHODS
    function updateEquipmentDataByOwnedEquipment() {
        for (var i=0; i<$scope.shopEquipmentList.length; i++) {
            for (var y=0; y<$rootScope.player.equipment.length; y++) {
                if ($scope.shopEquipmentList[i].name == $rootScope.player.equipment[y].name) {
                    $scope.shopEquipmentList[i].owned = true;
                    $scope.shopEquipmentList[i].isEquipped = $rootScope.player.equipment[y].is_equipped;
                }
            }
        }
    }

    function buy(equipment) {
        $http.post('/api/players/buyEquipment', {equipment_name: equipment.name}).
            then(function(response) {
                equipment.owned = true;
                $rootScope.player.equipment.push(response.data);
                $rootScope.player.cash -= equipment.cost;
                $scope.isEquipmentClicking = false;
            }, function(response) {
                $scope.isEquipmentClicking = false;
                alertError(response);
            });
    }

    function setEquippedState(equipment, value) {
        $http.post('/api/players/setEquippedState', {equipment_name: equipment.name, value: value}).
            then(function(response) {
                equipment.isEquipped = value;
                $scope.isEquipmentClicking = false;
            }, function(response) {
                $scope.isEquipmentClicking = false;
                alertError(response);
            });
    }

});