// shell > mongo twitter init.js

var collection = "tweets"
db.createCollection(collection);
db.getCollection(collection).createIndex({created_at: -1}, {name: 'created_at'});

// db.createUser({user: "admin", pwd: "111111", roles: ["readWrite"]});
