rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "srv-db-mongo-primary:27017" },
    { _id: 1, host: "srv-db-mongo-replica:27017" }
  ]
});
