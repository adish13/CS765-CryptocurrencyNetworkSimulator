pragma solidity ^0.8.19;

contract Payment {

    struct User {
        string name;
    }

    struct userAccounts {
        mapping(uint256 => uint256) contributions; // map to get contribution of user towards every other user (joint account) 
    }

    mapping(uint256 => User) private users;
    mapping(uint256 => userAccounts) private jointAccounts;

    // contract functions

    function registerUser(uint256 user_id, string memory userName) public {
        users[user_id] = User({ name: userName});
    }

    function createAcc(uint256 user_id_1, uint256 user_id_2, uint256 balance) public {
        // update contributions from both sides
        jointAccounts[user_id_1].contributions[user_id_2] = balance;
        jointAccounts[user_id_2].contributions[user_id_1] = balance;
    }

    function sendAmount(uint256 user_id_1, uint256 user_id_2) public {
        
        // assuming that client.py makes necessary checks before calling this function
        // update contributions
        jointAccounts[user_id_1].contributions[user_id_2] -= 1;
        jointAccounts[user_id_2].contributions[user_id_1] += 1;
    }

    function closeAccount(uint256 user_id_1, uint256 user_id_2) public {
        jointAccounts[user_id_1].contributions[user_id_2] = 0;
        jointAccounts[user_id_2].contributions[user_id_1] = 0;
    }

    function balances(uint256 user_id_1, uint256 user_id_2) public view returns (uint256) {
        // function to return balance of any node in any joint account
        return jointAccounts[user_id_1].contributions[user_id_2];
    }
}
