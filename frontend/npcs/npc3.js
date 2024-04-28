// npcs/npc3.js
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'npc3',
  brokers: ['localhost:19092'] // Your Kafka broker
});

const producer = kafka.producer();
const consumer = kafka.consumer({ groupId: 'npc3-group' });

module.exports = function (io) {
  const setupKafka = async () => {
    await producer.connect();
    await consumer.connect();
    await consumer.subscribe({ topic: 'npc3-response' });

    consumer.run({
      eachMessage: async ({ message }) => {
        io.emit('npc3-response', message.value.toString());
      },
    });
  };

  setupKafka();

  io.on('connection', (socket) => {
    socket.on('npc3-message', async (data) => {
      await producer.send({
        topic: 'npc3-request',
        messages: [
          { value: data.message }
        ],
      });
    });
  });
};
