module.exports = (sequelize, DataTypes) => (
    sequelize.define('inventory', {
        itemId: {
            type: DataTypes.INTEGER(1),
            allowNull: true,
        },
        state: {
            type: DataTypes.INTEGER(1),
            allowNull: true,
        },
    }, {
      timestamps: true,
      paranoid: true,
    })
  );