#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/types.h>
#include <asm/io.h>
#include <linux/loop.h>

#define LegionControllerVer "V0.3"

struct DEVICE_DATA
{
    uint64_t baseEC;
    uint16_t fanSpeedCurrentLeft;
    uint16_t fanSpeedCurrentRight;
    uint16_t tempCurrentCPU; // CPU temp
    uint16_t tempCurrentGPU; // GPU temp
    uint16_t fanCurveLeft[11];
    uint16_t fanCurveRight[11];
    //uint16_t tempCurveCPU[11];
    //uint16_t tempCurveGPU[11];
    uint8_t curveLen;
    uint8_t powerMode;
};

struct DEVICE_DATA GKCN =
    {
        .baseEC = 0xFE00D400,          // need to start at EC level
        .fanSpeedCurrentLeft = 0x200,  // 0x1FC
        .fanSpeedCurrentRight = 0x201, // 0x1FD
        .tempCurrentCPU = 0x138,
        .tempCurrentGPU = 0x139,
        .fanCurveLeft = {0x140, 0x141, 0x142, 0x143, 0x144, 0x145, 0x146, 0x147, 0x148, 0x149, 0x14A},
        .fanCurveRight = {0x150, 0x151, 0x152, 0x153, 0x154, 0x155, 0x156, 0x157, 0x158, 0x159, 0x15A},
        //.tempCurveCPU = {0x190, 0x191, 0x192, 0x193, 0x194, 0x195, 0x196, 0x197, 0x198, 0x199, 0x19A},
        //.tempCurveGPU = {0x1B0, 0x1B1, 0x1B2, 0x1B3, 0x1B4, 0x1B5, 0x1B6, 0x1B7, 0x1B8, 0x1B9, 0x1BA},
        .curveLen = 11,
        .powerMode = 0x20,

};

uint8_t *virt;
int i, pFanCurveLeft, pFanCurveRight;

static int cPowerMode = -1;
static int cFanCurveLeft = -1;
static int cFanCurveRight = -1;

module_param(cPowerMode, int, 0644);
module_param(cFanCurveLeft, int, 0644);
module_param(cFanCurveRight, int, 0644);

struct DEVICE_DATA *dev_data;

static struct kobject *LegionController;
static ssize_t sysfs_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf);
void writeFanCurveLeft(void);
void writeFanCurveRight(void);
void writePowerMode(void);

struct kobj_attribute fanSpeedCurrentLeft = __ATTR(fanSpeedCurrentLeft, 0444, sysfs_show, NULL);
struct kobj_attribute fanSpeedCurrentRight = __ATTR(fanSpeedCurrentRight, 0444, sysfs_show, NULL);
struct kobj_attribute tempCurrentCPU = __ATTR(tempCurrentCPU, 0444, sysfs_show, NULL);
struct kobj_attribute tempCurrentGPU = __ATTR(tempCurrentGPU, 0444, sysfs_show, NULL);
struct kobj_attribute fanCurveLeft = __ATTR(fanCurveLeft, 0444, sysfs_show, NULL);
//struct kobj_attribute fanCurveRight = __ATTR(fanCurveRight, 0444, sysfs_show, NULL);
//struct kobj_attribute tempCurveCPU = __ATTR(tempCurveCPU, 0444, sysfs_show, NULL);
//struct kobj_attribute tempCurveGPU = __ATTR(tempCurveGPU, 0444, sysfs_show, NULL);
struct kobj_attribute powerMode = __ATTR(powerMode, 0444, sysfs_show, NULL);

static ssize_t sysfs_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf)
{
    if (attr == &fanSpeedCurrentLeft)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->fanSpeedCurrentLeft));
    }
    if (attr == &fanSpeedCurrentRight)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->fanSpeedCurrentRight));
    }
    if (attr == &tempCurrentCPU)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->tempCurrentCPU));
    }
    if (attr == &tempCurrentGPU)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->tempCurrentGPU));
    }

    if (attr == &powerMode)
    {
        writePowerMode();
        
        writeFanCurveLeft();

        writeFanCurveRight();

        
        if (*(virt + dev_data->powerMode) == 0)
        {
            return sprintf(buf, "%d\n", 0);
        }
        else if (*(virt + dev_data->powerMode) == 1)
        {
            return sprintf(buf, "%d\n", 1);
        }
        else if (*(virt + dev_data->powerMode) == 2)
        {
            return sprintf(buf, "%d\n", 2);
        }
    }

    if (attr == &fanCurveLeft)
    {
        return sprintf(buf, "%d %d %d %d %d %d %d %d %d %d %d\n",
                       *(virt + dev_data->fanCurveLeft[0]),
                       *(virt + dev_data->fanCurveLeft[1]),
                       *(virt + dev_data->fanCurveLeft[2]),
                       *(virt + dev_data->fanCurveLeft[3]),
                       *(virt + dev_data->fanCurveLeft[4]),
                       *(virt + dev_data->fanCurveLeft[5]),
                       *(virt + dev_data->fanCurveLeft[6]),
                       *(virt + dev_data->fanCurveLeft[7]),
                       *(virt + dev_data->fanCurveLeft[8]),
                       *(virt + dev_data->fanCurveLeft[9]),
                       *(virt + dev_data->fanCurveLeft[10]));
    }
/*
    if (attr == &fanCurveRight)
    {
        for (i = 0; i < 10; i++)
        {
            if (cFanCurveRight >= 0 && cFanCurveRight != pFanCurveRight && cFanCurveRight <= 45)
            {
                *(virt + dev_data->fanCurveRight[i]) = cFanCurveRight;
                cFanCurveRight = -1;
            }
        }
        pFanCurveRight = cFanCurveRight;

          
        findPowerMode();

        if (powerModeCurrent == 0)
        {
            return sprintf(buf, "%d %d %d %d %d %d\n",
                           *(virt + dev_data->fanCurveRight[0]),
                           *(virt + dev_data->fanCurveRight[1]),
                           *(virt + dev_data->fanCurveRight[3]),
                           *(virt + dev_data->fanCurveRight[5]),
                           *(virt + dev_data->fanCurveRight[7]),
                           *(virt + dev_data->fanCurveRight[8]));
        }
        else if (powerModeCurrent == 1)
        {
            return sprintf(buf, "%d %d %d %d %d %d\n",
                           *(virt + dev_data->fanCurveRight[0]),
                           *(virt + dev_data->fanCurveRight[1]),
                           *(virt + dev_data->fanCurveRight[3]),
                           *(virt + dev_data->fanCurveRight[5]),
                           *(virt + dev_data->fanCurveRight[7]),
                           *(virt + dev_data->fanCurveRight[9]));
        }
        else if (powerModeCurrent == 2)
        {
            return sprintf(buf, "%d %d %d %d %d %d\n",
                           *(virt + dev_data->fanCurveRight[0]),
                           *(virt + dev_data->fanCurveRight[1]),
                           *(virt + dev_data->fanCurveRight[3]),
                           *(virt + dev_data->fanCurveRight[5]),
                           *(virt + dev_data->fanCurveRight[6]),
                           *(virt + dev_data->fanCurveRight[7]));
        }
    }
/*
    if (attr == &tempCurveCPU)
    {
        
        for (i = 0; i < 10; i++)
        {
            if (cTempCurveCPU[i] >= 0 && cTempCurveCPU[i] != *(virt + dev_data->tempCurveCPU[i]) && cTempCurveCPU[i] <= 105)
            {
                *(virt + dev_data->tempCurveCPU[i]) = cTempCurveCPU[i];
                cTempCurveCPU[i] = -1;
            }
        }
        

        findPowerMode();

        if (powerModeCurrent == 0)
        {
            return sprintf(buf, "%d %d %d %d %d %d\n",
                           *(virt + dev_data->tempCurveCPU[0]),
                           *(virt + dev_data->tempCurveCPU[1]),
                           *(virt + dev_data->tempCurveCPU[3]),
                           *(virt + dev_data->tempCurveCPU[5]),
                           *(virt + dev_data->tempCurveCPU[7]),
                           *(virt + dev_data->tempCurveCPU[8]));
        }
        else if (powerModeCurrent == 1)
        {
            return sprintf(buf, "%d %d %d %d %d %d\n",
                           *(virt + dev_data->tempCurveCPU[0]),
                           *(virt + dev_data->tempCurveCPU[1]),
                           *(virt + dev_data->tempCurveCPU[3]),
                           *(virt + dev_data->tempCurveCPU[5]),
                           *(virt + dev_data->tempCurveCPU[7]),
                           *(virt + dev_data->tempCurveCPU[9]));
        }
        else if (powerModeCurrent == 2)
        {
            return sprintf(buf, "%d %d %d %d %d %d\n",
                           *(virt + dev_data->tempCurveCPU[0]),
                           *(virt + dev_data->tempCurveCPU[1]),
                           *(virt + dev_data->tempCurveCPU[3]),
                           *(virt + dev_data->tempCurveCPU[5]),
                           *(virt + dev_data->tempCurveCPU[6]),
                           *(virt + dev_data->tempCurveCPU[7]));
        }
    }

    if (attr == &tempCurveGPU)
    {
        
        for (i = 0; i < 10; i++)
        {
            if (cTempCurveGPU[i] >= 0 && cTempCurveCPU[i] != *(virt + dev_data->tempCurveGPU[i]) && cTempCurveGPU[i] <= 75)
            {
                *(virt + dev_data->tempCurveGPU[i]) = cTempCurveGPU[i];
                cTempCurveGPU[i] = -1;
            }
        }
        

        findPowerMode();
        
        if (powerModeCurrent == 0)
        {
            return sprintf(buf, "%d %d %d %d %d %d\n",
                           *(virt + dev_data->tempCurveGPU[0]),
                           *(virt + dev_data->tempCurveGPU[1]),
                           *(virt + dev_data->tempCurveGPU[3]),
                           *(virt + dev_data->tempCurveGPU[5]),
                           *(virt + dev_data->tempCurveGPU[7]),
                           *(virt + dev_data->tempCurveGPU[8]));
        }
        else if (powerModeCurrent == 1)
        {
            return sprintf(buf, "%d %d %d %d %d %d\n",
                           *(virt + dev_data->tempCurveGPU[0]),
                           *(virt + dev_data->tempCurveGPU[1]),
                           *(virt + dev_data->tempCurveGPU[3]),
                           *(virt + dev_data->tempCurveGPU[5]),
                           *(virt + dev_data->tempCurveGPU[7]),
                           *(virt + dev_data->tempCurveGPU[9]));
        }
        else if (powerModeCurrent == 2)
        {
            return sprintf(buf, "%d %d %d %d %d %d\n",
                           *(virt + dev_data->tempCurveGPU[0]),
                           *(virt + dev_data->tempCurveGPU[1]),
                           *(virt + dev_data->tempCurveGPU[3]),
                           *(virt + dev_data->tempCurveGPU[5]),
                           *(virt + dev_data->tempCurveGPU[6]),
                           *(virt + dev_data->tempCurveGPU[7]));
        }
    } */

    return 0;
}


void writeFanCurveLeft(void)
{
    for (i = 0; i < dev_data->curveLen; i++)
    {
        if (cFanCurveLeft >= 0 && cFanCurveLeft != pFanCurveLeft && cFanCurveLeft <= 45)
        {
            *(virt + dev_data->fanCurveLeft[i]) = cFanCurveLeft;
        }
    }
    cFanCurveLeft = -1;

    pFanCurveLeft = cFanCurveLeft;
}

void writeFanCurveRight(void)
{
    for (i = 0; i < dev_data->curveLen; i++)
    {
        if (cFanCurveRight >= 0 && cFanCurveRight != pFanCurveRight && cFanCurveRight <= 45)
        {
            *(virt + dev_data->fanCurveRight[i]) = cFanCurveRight;
        }
    }
    cFanCurveRight = -1;

    pFanCurveRight = cFanCurveRight;
}

void writePowerMode(void)
{
    if (cPowerMode >= 0 && cPowerMode != *(virt + dev_data->powerMode) && cPowerMode <= 2)
    {
        *(virt + dev_data->powerMode) = cPowerMode;
    }
    cPowerMode = -1;
}

int init_module(void)
{
    dev_data = &GKCN;
    int error = 0;
    pr_info("Legion Controller %s Loaded \n", LegionControllerVer);
    virt = (ioremap(dev_data->baseEC, 0xFF * 3));
    pr_info("Succefful Mapped EC (Virtual Address 0x%p)\n", virt);

    pr_info("Creating sysfs inteface over /sys/kernel/LegionController/");
    LegionController = kobject_create_and_add("LegionController",
                                              kernel_kobj);
    if (!LegionController)
        return -ENOMEM;

    error = sysfs_create_file(LegionController, &fanSpeedCurrentLeft.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/fanSpeedCurrentLeft \n");
    }
    error = sysfs_create_file(LegionController, &fanSpeedCurrentRight.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/fanSpeedCurrentRight \n");
    }
    error = sysfs_create_file(LegionController, &tempCurrentCPU.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/tempCurrentCPU \n");
    }
    error = sysfs_create_file(LegionController, &tempCurrentGPU.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/tempCurrentGPU \n");
    }
    error = sysfs_create_file(LegionController, &fanCurveLeft.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    } /*
    error = sysfs_create_file(LegionController, &fanCurveRight.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    }
    error = sysfs_create_file(LegionController, &tempCurveCPU.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    }
    error = sysfs_create_file(LegionController, &tempCurveGPU.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    } */
    error = sysfs_create_file(LegionController, &powerMode.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    }

    pr_info("Creating hwmon binding");

    /* A non 0 return means init_module failed; module can't be loaded. */
    return 0;
}

void cleanup_module(void)

{
    kobject_put(LegionController);
    pr_info("Legion Fan %s Unloaded \n", LegionControllerVer);
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("NUTSU7");
MODULE_DESCRIPTION("LEGION");
