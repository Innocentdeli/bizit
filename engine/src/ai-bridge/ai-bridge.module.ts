import { Module } from '@nestjs/common';
import { AiBridgeService } from './ai-bridge.service';
import { AiBridgeController } from './ai-bridge.controller';

@Module({
  controllers: [AiBridgeController],
  providers: [AiBridgeService],
  exports: [AiBridgeService],
})
export class AiBridgeModule {}
