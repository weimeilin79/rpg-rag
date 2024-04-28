// npcs/npc1.js
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'npc1',
  brokers: ['localhost:19092'] // Your Kafka broker
});

const producer = kafka.producer();
const consumer = kafka.consumer({ groupId: 'npc1-group' });

module.exports = function (io) {
  const setupKafka = async () => {
    await producer.connect();
    await consumer.connect();
    await consumer.subscribe({ topic: 'npc1-response' });

    consumer.run({
      eachMessage: async ({ message }) => {
        io.emit('npc1-response', message.value.toString());
      },
    });
  };

  setupKafka();

  io.on('connection', (socket) => {
    socket.on('npc1-message', async (data) => {
      await producer.send({
        topic: 'npc1-request',
        messages: [
          { value: data.message }
        ],
      });
    });
  });
};
