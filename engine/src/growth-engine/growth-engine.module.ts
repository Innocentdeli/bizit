import { Module } from '@nestjs/common';
import { GrowthEngineService } from './growth-engine.service';
import { GrowthEngineController } from './growth-engine.controller';
import { PrismaService } from '../prisma.service';

@Module({
  providers: [GrowthEngineService, PrismaService],
  controllers: [GrowthEngineController],
  exports: [GrowthEngineService],
})
export class GrowthEngineModule {}
