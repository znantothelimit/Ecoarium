module.exports = (sequelize, DataTypes) => (
    sequelize.define('user', {
      user_id: {
        type: DataTypes.STRING(40),
        allowNull: true,
        unique: true,
      },
      password: {
        type: DataTypes.STRING(100),
        allowNull: true,
      },
      nickname:{
        type: DataTypes.STRING(20),
        allowNull: true,
      },
      points:{
        type: DataTypes.INTEGER(1),
        allowNull: true,
      },
      barcode:{
        type: DataTypes.BIGINT,
        allowNull: true,
      },
      admin:{
        type: DataTypes.INTEGER(1),
        allowNull: true,
      },
    }, {
      timestamps: true,
      paranoid: true,
    })
  );