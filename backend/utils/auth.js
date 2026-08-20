const jwt = require('jsonwebtoken');
const { User, Role } = require('../models');

const SECRET_KEY = process.env.SECRET_KEY || 'dev_secret';

const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) return res.status(401).json({ msg: 'No token provided' });

  jwt.verify(token, SECRET_KEY, async (err, decoded) => {
    if (err) return res.status(403).json({ msg: 'Invalid token' });
    
    const user = await User.findByPk(parseInt(decoded.sub), {
      include: [{ model: Role, as: 'role' }]
    });
    
    if (!user) return res.status(403).json({ msg: 'User not found' });
    
    req.user = user;
    next();
  });
};

const authorizeRole = (roleNames) => {
  return (req, res, next) => {
    if (!roleNames.includes(req.user.role.name)) {
      return res.status(403).json({ msg: 'Unauthorized access' });
    }
    next();
  };
};

module.exports = { authenticateToken, authorizeRole };
