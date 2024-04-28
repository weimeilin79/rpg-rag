// npcs/npc2.js
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'npc2',
  brokers: ['localhost:19092'] // Your Kafka broker
});

const producer = kafka.producer();
const consumer = kafka.consumer({ groupId: 'npc2-group' });

module.exports = function (io) {
  const setupKafka = async () => {
    await producer.connect();
    await consumer.connect();
    await consumer.subscribe({ topic: 'npc2-response' });

    consumer.run({
      eachMessage: async ({ message }) => {
        io.emit('npc2-response', message.value.toString());
      },
    });
  };

  setupKafka();

  io.on('connection', (socket) => {
    socket.on('npc2-message', async (data) => {
      await producer.send({
        topic: 'npc2-request',
        messages: [
          { value: data.message }
        ],
      });
    });
  });
};
