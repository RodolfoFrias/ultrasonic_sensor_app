import { Router } from 'express';
import { notifyUser } from './Users';


// User-route
const userRouter = Router();
userRouter.post('/notification', notifyUser);

// Export the base-router
const baseRouter = Router();
baseRouter.use('/iot', userRouter);
export default baseRouter;
