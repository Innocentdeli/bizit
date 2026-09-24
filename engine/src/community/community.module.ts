import { Module } from '@nestjs/common';
import { CommunityGateway } from './community.gateway';
import { CommunityService } from './community.service';
import { CommunityController } from './community.controller';
import { PrismaService } from '../prisma.service';

@Module({
  controllers: [CommunityController],
  providers: [CommunityGateway, CommunityService, PrismaService],
})
export class CommunityModule {}
