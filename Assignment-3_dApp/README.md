CS-765 Assignment3

Instructions to compile and run: 

1) initialize truffle : truffle init
2) Move Payment.sol to contracts folder
3) Move 2_deploy_migrations.js to migrations folder
4) UnComment the lines 67-71 (developement) in truffle-config.js 
4) compile smart contract : truffle compile
5) Start ganache-cli in a new terminal : ganache-cli
6) deploy smart contract : truffle migrate
7) copy address of smart contract from ganache-cli into client.py
8) run client.py: python3 client.py
