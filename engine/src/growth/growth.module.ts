import { Module } from '@nestjs/common';
import { GrowthService } from './growth.service';
import { GrowthController } from './growth.controller';
import { PrismaService } from '../prisma.service';

@Module({
  controllers: [GrowthController],
  providers: [GrowthService, PrismaService],
  exports: [GrowthService],
})
export class GrowthModule {}
